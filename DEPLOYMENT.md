# Penny Wise - Deployment Guide 🚀

This guide will help you deploy **Penny Wise** to the web for free and install it on your Android phone.

## 1. Cloud Hosting (Free)

We will use **Streamlit Community Cloud** for hosting the app and a free MySQL provider for the database.

### Step A: Database (Free MySQL)
You need a cloud database. **TiDB Cloud** or **Aiven** offer excellent free tiers.

1.  **Sign Up**: Go to [TiDB Cloud](https://tidbcloud.com/) or [Aiven](https://aiven.io/) and create a free account.
2.  **Create Cluster**: Create a standard MySQL compatible cluster (Free Tier).
3.  **Get Credentials**: note down the:
    *   Host (e.g., `gateway01.us-west-2.prod.aws.tidbcloud.com`)
    *   Port (e.g., `4000`)
    *   User
    *   Password
    *   Database Name
4.  **Initialize Tables**:
    *   Connect to your cloud database using a tool like **DBeaver** or **HeidiSQL**.
    *   Run the contents of [schema.sql](schema.sql) to create the tables.

### Step B: Deploy App
1.  **Sign Up**: Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2.  **New App**: Click **"New app"**.
3.  **Select Repo**: Choose `jabert007/budget_planner_app`.
4.  **Main File Path**: Enter `app.py`.
5.  **Advanced Settings (Secrets)**:
    *   Click "Advanced settings" -> "Secrets".
    *   Paste your database credentials in TOML format:
    ```toml
    [mysql]
    host = "your-cloud-db-host"
    user = "your-db-user"
    password = "your-db-password"
    database = "your-db-name"
    port = 4000
    ```
6.  **Deploy**: Click **"Deploy!"**.
    *   *Wait 2-3 minutes. Your app is now live on the internet!*

---

## 2. Android App (Web2App) 📱

To get this as an app on your phone:

**Option A: Chrome "Add to Home Screen" (Easiest)**
1.  Open your new Streamlit App URL in Chrome on Android.
2.  Tap the **Examples menu** (3 dots) -> **Add to Home Screen**.
3.  It will appear as an App Icon ("Penny Wise") on your launcher.

**Option B: Native APK (Webview)**
If you want a real `.apk` file:
1.  Go to [AppsGeyser](https://appsgeyser.com/create-url-app/) (or any Web-to-App converter).
2.  **Website URL**: Paste your deployed Streamlit URL.
3.  **Name**: Penny Wise.
4.  **Icon**: Upload `images/logo.png`.
5.  **Download**: Get the APK and install it on your phone.

---

## 3. Maintenance

*   **Updates**: Any changes you push to GitHub will automatically update the live site!
*   **Data**: Your data is safe in the Cloud Database, even if you redeploy the app.
