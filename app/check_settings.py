from app.core.config import settings

def main():
    print("App Name:",settings.app_name)
    print("Environment:", settings.environment)
    print("Version:", settings.version)


if __name__ == "__main__":
        main()