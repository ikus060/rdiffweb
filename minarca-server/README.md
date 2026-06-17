![Minarca Logo](https://gitlab.com/ikus-soft/minarca/-/raw/master/doc/_static/banner.png)


<p align="center">
  <strong>
    <a href="https://minarca.org">website</a>
    •
    <a href="https://www.ikus-soft.com/en/minarca/doc">docs</a>
    •
    <a href="https://minarca.org/contactus">newsletter</a>
  </strong>
</p>

<h1 align="center">
  Welcome to Minarca Backup Software!
</h1>

# Minarca Server

Minarca Server is the **server-side component** of Minarca, a **free and open-source backup solution** designed for small businesses and service providers. It offers a simple, self-hosted way to manage backups with an intuitive **web interface** for browsing and restoring files.

## Features

- **Web Interface**: Easily restore files from anywhere.
- **End-to-End Integration**: Built on [rdiffweb](https://rdiffweb.org/) for robust file versioning.
- **Self-Hosted**: Stay in control of your backup strategy.

## Installation

To install Minarca Server:

1. Add the APT repository:
   ```sh
   curl -L https://www.ikus-soft.com/archive/minarca/public.key | gpg --dearmor > /usr/share/keyrings/minarca-keyring.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/minarca-keyring.gpg] https://nexus.ikus-soft.com/repository/apt/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/minarca.list
   apt update
   ```
2. Install the server:
   ```sh
   apt install minarca-server
   ```

For detailed installation instructions, see the [Minarca Server Documentation](https://www.ikus-soft.com/archive/minarca/doc/installation.html).

## Getting Started

Try Minarca Server without installation! Access our demo environment at <https://test.minarca.net> using:

- **Username**: admin  
- **Password**: admin123  

## Contribution

We welcome contributions to improve Minarca Server. You can help by:

- Reporting issues on our [GitLab repository](https://gitlab.com/ikus-soft/minarca/issues).
- Contributing to translations or platform support.
- Suggesting or implementing new features.

## Professional Support

Need help setting up or managing Minarca Server? [Contact us](https://minarca.org/contactus) for professional support options.

## About Minarca Server

Minarca Server is developed by [IKUS Software inc.](https://ikus-soft.com) and is licensed under the **GNU AGPLv3**. 

**Source Code**:  
- [Minarca Client](https://gitlab.com/ikus-soft/minarca)  
- [Minarca Quota Api](https://gitlab.com/ikus-soft/minarca-quota-api)

For more information, visit the [Minarca Website](https://minarca.org).
