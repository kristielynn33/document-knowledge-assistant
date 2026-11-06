from pathlib import Path

from dotenv import dotenv_values
from google import genai
from google.genai import errors, types


PROJECT_FOLDER = Path(__file__).resolve().parent


def main() -> int:
    """List text-generation models without sending documents."""

    settings = dotenv_values(PROJECT_FOLDER / ".env")
    api_key = (settings.get("GEMINI_API_KEY") or "").strip()

    if not api_key or api_key == "PASTE_YOUR_KEY_HERE":
        print("NOT READY: Add your API key to the local .env file.")
        return 1

    print("This requests Google's model list.")
    print("It does not read or send your policy documents.")

    try:
        permission = input(
            "Type LIST to request the model list: "
        ).strip()

        if permission != "LIST":
            print("STOPPED: No request was sent.")
            return 1

        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        ) as client:
            names = []

            for model in client.models.list():
                if (
                    model.name
                    and "generateContent" in (model.supported_actions or [])
                ):
                    names.append(model.name)

    except (EOFError, KeyboardInterrupt):
        print("\nSTOPPED by user.")
        return 1

    except errors.APIError as error:
        print(f"FAILED: Model listing returned status {error.code}.")
        return 1

    except Exception as error:
        print(f"FAILED: Model listing raised {type(error).__name__}.")
        return 1

    if not names:
        print("No generation models were listed.")
        return 1

    print("\nSUCCESS: Generation models listed:")

    for name in sorted(names):
        print(name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())