from pathlib import Path

from dotenv import dotenv_values
from google import genai
from google.genai import errors, types


PROJECT_FOLDER = Path(__file__).resolve().parent


def main() -> int:
    """Test Gemini with a harmless prompt, without reading documents."""

    settings = dotenv_values(PROJECT_FOLDER / ".env")

    api_key = (settings.get("GEMINI_API_KEY") or "").strip()
    model_name = (settings.get("GEMINI_MODEL") or "").strip()

    if not api_key or api_key == "PASTE_YOUR_KEY_HERE":
        print("NOT READY: Add your API key to the local .env file.")
        return 1

    if not model_name:
        print("NOT READY: Add GEMINI_MODEL to the local .env file.")
        return 1

    print("This test sends a short greeting request to Gemini.")
    print("It does not read or send your policy documents.")

    try:
        permission = input(
            "Type SEND to make one test request: "
        ).strip()

        if permission != "SEND":
            print("STOPPED: No request was sent.")
            return 1

        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=90000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        ) as client:
            response = client.models.generate_content(
                model=model_name,
                contents=(
                    "Reply with exactly this text and nothing else: "
                    "CONNECTION_OK"
                ),
            )

            reply = (response.text or "").strip()

    except (EOFError, KeyboardInterrupt):
        print("\nSTOPPED by user.")
        return 1

    except errors.APIError as error:
        # Report the status without printing credentials or the request.
        print(f"FAILED: Gemini API returned status {error.code}.")
        return 1

    except Exception as error:
        print(f"FAILED: connection test raised {type(error).__name__}.")
        return 1

    if not reply:
        print("FAILED: Gemini returned no text.")
        return 1

    print("SUCCESS: Gemini connection worked.")
    print(f"Model: {model_name}")
    print(f"Gemini response: {reply}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())