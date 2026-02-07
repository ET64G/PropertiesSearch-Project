from config import load_config

def main() -> None:
    config = load_config()
    print("Config loaded OK")
    print("Email from::", config.smtp.email_from)

if __name__ == "__main__":
    main()


