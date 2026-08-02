import os
import json
import subprocess
from typing import Dict, Any, List

import requests


class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _validate_embeddings(self, model: str, texts: List[str], embeddings: List[Any]) -> List[List[float]]:
        if len(embeddings) != len(texts):
            raise ValueError(
                f"Embedding count mismatch for model {model}: expected {len(texts)}, got {len(embeddings)}"
            )
        result: List[List[float]] = []
        for i, emb in enumerate(embeddings):
            if not isinstance(emb, list) or not emb:
                raise ValueError(f"Invalid embedding for input {i}: {emb!r}")
            result.append(emb)
        return result

    def _parse_embedding_response(self, model: str, texts: List[str], data: Any) -> List[List[float]]:
        if isinstance(data, dict):
            if "embedding" in data:
                emb = data["embedding"]
                if not emb:
                    raise ValueError(f"Ollama returned empty embedding for model {model}")
                if isinstance(emb[0], list):
                    return self._validate_embeddings(model, texts, emb)
                return [emb for _ in texts]
            if "embeddings" in data:
                return self._validate_embeddings(model, texts, data["embeddings"])
            if "data" in data and isinstance(data["data"], list):
                return self._validate_embeddings(
                    model,
                    texts,
                    [item.get("embedding") for item in data["data"]],
                )

        if isinstance(data, list):
            return self._validate_embeddings(model, texts, data)

        raise ValueError(f"Unexpected embedding response from Ollama: {data}")

    def _ollama_run_embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for text in texts:
            command = [
                "ollama",
                "run",
                model,
                "--format",
                "json",
                "--dimensions",
                "768",
                text,
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"ollama run failed for model {model}: {result.stderr.strip() or result.stdout.strip()}"
                )

            try:
                parsed = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Unable to parse ollama run output for model {model}: {result.stdout!r}"
                ) from exc

            if not isinstance(parsed, list):
                raise ValueError(
                    f"Unexpected ollama run output shape for model {model}: {parsed!r}"
                )
            embeddings.append(parsed)

        return self._validate_embeddings(model, texts, embeddings)

    def embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "input": texts},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_embedding_response(model, texts, data)
        except (requests.RequestException, ValueError) as first_exc:
            try:
                return self._ollama_run_embeddings(model, texts)
            except Exception as fallback_exc:
                raise RuntimeError(
                    f"Ollama embeddings failed via HTTP and fallback: {first_exc}; {fallback_exc}"
                ) from fallback_exc

    def list_running_models(self) -> List[str]:
        try:
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            if result.returncode != 0:
                return []

            models: List[str] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("NAME"):
                    continue
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models
        except Exception:
            return []

    def list_available_models(self) -> List[str]:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            if result.returncode != 0:
                return []

            models: List[str] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("NAME"):
                    continue
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models
        except Exception:
            return []

    def stop_all_models(self) -> List[str]:
        stopped: List[str] = []
        for model in self.list_running_models():
            if self.stop_model(model):
                stopped.append(model)
        return stopped

    def stop_model(self, model: str) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "stop", model],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def chat(self, model: str, messages: List[Dict[str, str]], timeout: int = 60) -> str:
        # Try a list of possible chat endpoints in case Ollama exposes a different path
        endpoints = [
            f"{self.base_url}/api/chat",
            f"{self.base_url}/chat",
            f"{self.base_url}/api/v1/chat",
            f"{self.base_url}/v1/chat",
            f"{self.base_url}/api/chat/completions",
            f"{self.base_url}/chat/completions",
            f"{self.base_url}/api/v1/chat/completions",
            f"{self.base_url}/v1/chat/completions",
        ]

        last_resp = None
        last_exception = None
        payload = {"model": model, "messages": messages}
        for endpoint in endpoints:
            # First try a non-streaming POST (some Ollama deployments may expect this)
            try:
                resp = requests.post(endpoint, json=payload, timeout=timeout)
            except requests.RequestException as exc:
                last_exception = exc
                continue

            last_resp = resp
            if resp.status_code == 404:
                body = None
                try:
                    body = resp.text
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
                except Exception:
                    data = None
                finally:
                    resp.close()

                if isinstance(data, dict) and data.get("error"):
                    raise requests.HTTPError(f"{resp.status_code} response from {endpoint}: {data}")

                continue

            if resp.status_code >= 400:
                body = None
                try:
                    body = resp.text
                except Exception:
                    body = "<unable to read body>"
                resp.close()
                raise requests.HTTPError(f"{resp.status_code} response from {endpoint}: {body}")

            # If we got a 200, check if response contains full JSON or streaming chunks
            text = resp.text
            # If text looks like concatenated JSON objects separated by newlines
            lines = [ln for ln in text.splitlines() if ln.strip()]
            collected: List[str] = []
            for ln in lines:
                try:
                    obj = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    part = obj.get("message", {}).get("content")
                    if part:
                        collected.append(part)
                    if obj.get("done"):
                        break

            if collected:
                resp.close()
                return "".join(collected)

            # If not, make a streaming request to capture chunked responses
            try:
                resp.close()
                stream_resp = requests.post(endpoint, json=payload, timeout=timeout, stream=True)
            except requests.RequestException as exc:
                last_exception = exc
                continue

            last_resp = stream_resp
            if stream_resp.status_code == 404:
                try:
                    stream_resp.close()
                except Exception:
                    pass
                continue

            if stream_resp.status_code >= 400:
                body = None
                try:
                    body = stream_resp.text
                except Exception:
                    body = "<unable to read body>"
                stream_resp.close()
                raise requests.HTTPError(f"{stream_resp.status_code} response from {endpoint}: {body}")

            for line in stream_resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    part = obj.get("message", {}).get("content")
                    if part:
                        collected.append(part)
                    if obj.get("done"):
                        break

            if collected:
                stream_resp.close()
                return "".join(collected)

            try:
                data = stream_resp.json()
            except ValueError:
                data = {}
            finally:
                stream_resp.close()

            if isinstance(data, dict):
                msg = data.get("message")
                if isinstance(msg, dict):
                    return msg.get("content") or ""
                if isinstance(msg, str):
                    return msg

            return str(data)

        # If we get here, all endpoints failed
        if last_resp is not None:
            try:
                body = last_resp.text
            except Exception:
                body = "<unable to read body>"
            raise requests.HTTPError(f"All chat endpoints returned error. Last status={last_resp.status_code}, body={body}")
        if last_exception is not None:
            raise last_exception
        raise RuntimeError("Unable to contact Ollama chat endpoints")


def get_client(config: Dict[str, Any]) -> OllamaClient:
    return OllamaClient(config["ollama_url"])
