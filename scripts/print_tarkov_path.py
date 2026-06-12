from tarkov_tool.tarkov import path

if __name__ == "__main__":
    print("Install folder:", path.install_folder())
    print("Logs folder:", path.logs_folder())
    print("Screenshots folder:", path.screenshots_folder())
    print("Temp folder:", path.temp_folder())
