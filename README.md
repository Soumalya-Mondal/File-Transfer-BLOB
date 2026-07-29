<div align="center">

# 📦 File-Transfer-BLOB

**A lightweight Python CLI tool for secure file upload, download & removal with Azure Blob Storage**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0089D6?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/services/storage/blobs/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📑 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Tech Stack](#-tech-stack)
- [How It Works](#-how-it-works)
- [Development](#-development)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **🔼 Upload, 🔽 Download & 🗑️ Remove** — Interactive mode to upload files to Azure Blob Storage, download blobs locally, or remove all blobs from the container.
- **🔒 MD5 Integrity Verification** — Every file gets its MD5 hash calculated before upload and verified after both upload and download, ensuring data integrity.
- **⚠️ Conflict Handling** — Detects existing files/blobs and prompts the user before overwriting or deleting.
- **📁 Batch Processing** — Automatically processes all files inside the `FilesUpload` folder or downloads all blobs from the container at once.
- **🎨 Styled Terminal Output** — Clean, color-coded logs with separators for easy reading.
- **🔐 Environment-Based Configuration** — Uses a `.env` file for secure credential management.
- **📂 Auto Directory Creation** — `FilesUpload` and `FilesDownload` folders are created automatically if they don't exist.

---

## 🏗️ Project Structure

```
File-Transfer-BLOB/
├── .env                     # Environment variables (not committed)
├── .gitignore               # Git ignore rules
├── .python-version          # Python version specifier (3.12)
├── main.py                  # Main application script
├── pyproject.toml           # Project metadata & dependencies
├── uv.lock                  # uv lockfile for reproducible installs
├── FilesUpload/             # Place files here to upload (auto-created, gitignored)
│   └── (your files)
└── FilesDownload/           # Downloaded blobs appear here (auto-created, gitignored)
    └── (your files)
```

> 💡 **Note:** `FilesUpload/` and `FilesDownload/` are automatically created on first run and are listed in `.gitignore` so your data never gets committed.

---

## 🚀 Quick Start

### Prerequisites

- [Python](https://www.python.org/downloads/) **3.12+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- An [Azure Storage Account](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create) with a blob container

### 1. Clone the Repository

```bash
git clone <repository-url>
cd File-Transfer-BLOB
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root with your Azure credentials:

```env
BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
BLOB_CONTAINER_NAME="your-container-name"
```

> ⚠️ **Never commit your `.env` file!** It is already listed in `.gitignore`.

### 4. Run the Application

```bash
uv run main.py
```

You will be prompted to choose:

```
Please Choose Operation (U for Upload / D for Download / R for Remove):
```

---

## 📖 Usage Guide

### Uploading Files

1. Place the files you want to upload inside the **`FilesUpload/`** directory.
2. Run the script and choose **U**.
3. The tool will loop through all files and upload them to the configured container.
4. If a blob with the same name already exists, it will ask if you want to replace it.

### Downloading Files

1. Run the script and choose **D**.
2. The tool will list all available blobs in the container.
3. Each blob will be downloaded into the **`FilesDownload/`** directory.
4. If a local file with the same name exists, it will ask if you want to overwrite it.

### Removing Files

1. Run the script and choose **R**.
2. The tool will list all blobs currently in the container.
3. Confirm the bulk deletion by entering **Y**.
4. All listed blobs will be deleted from the container.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| [Python 3.12](https://www.python.org/) | Core language |
| [azure-storage-blob](https://pypi.org/project/azure-storage-blob/) | Azure Blob Storage SDK |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |
| [uv](https://docs.astral.sh/uv/) | Fast Python package & project manager |

---

## ⚙️ How It Works

### Upload Flow

```
FilesUpload/  ──►  Calculate MD5  ──►  Upload to Azure  ──►  Verify Size & MD5
```

### Download Flow

```
Azure Blobs  ──►  Download to FilesDownload/  ──►  Verify Size & MD5
```

### Remove Flow

```
Azure Blobs  ──►  List All Blobs  ──►  Confirm With User  ──►  Delete All Blobs
```

### Integrity Verification

The tool computes an **MD5 hash** for every file and stores it as blob metadata during upload. After both upload and download, it compares:

- **File size** (local vs. remote)
- **MD5 hash** (local vs. remote metadata)

If both match, the operation is reported as successful. ✅

---

## 🧪 Development

### Running in Development Mode

```bash
uv run main.py
```

### Adding New Dependencies

```bash
uv add <package-name>
```

### Updating Lockfile

```bash
uv lock
```

---

## 📝 Environment Variables

| Variable | Description |
|----------|-------------|
| `BLOB_CONNECTION_STRING` | Azure Blob Storage connection string |
| `BLOB_CONTAINER_NAME` | Name of the target blob container |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [**MIT License**](LICENSE).

---

<div align="center">

Made with ❤️ using Python & Azure

</div>
