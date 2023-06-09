# Installing and Configuring Fail2Ban for Secure SSH Server

Fail2Ban is a powerful open-source intrusion prevention tool that helps protect your SSH server by automatically blocking IP addresses that exhibit suspicious behavior, such as repeated failed login attempts. Follow these steps to install and configure Fail2Ban to secure your SSH server:

## Step 1: Install Fail2Ban

1. Update your package manager's repository:

    ```sh
    sudo apt update
    ```

2. Install Fail2Ban:

    ```sh
    sudo apt install fail2ban
    ```

## Step 2: Configure Fail2Ban

1. Create a new configuration file:

    ```sh
    sudo touch /etc/fail2ban/jail.local
    ```

2. Open the `jail.local` file using a text editor:

    ```sh
    sudo nano /etc/fail2ban/jail.local
    ```

3. Configure the `[sshd]` section to secure SSH server:

    ```ini
    [sshd]
    enabled = true
    ```

4. Save the changes and exit the text editor (press Ctrl + X, then Y, and finally Enter).

## Step 3: Start and Enable Fail2Ban

1. Start the Fail2Ban service:

    ```sh
    sudo systemctl start fail2ban
    ```

2. Enable Fail2Ban to start on system boot:

    ```sh
    sudo systemctl enable fail2ban
    ```

## Customize Fail2Ban Rules

If you want to customize Fail2Ban rules or create specific filters for your SSH server, you can edit the `jail.local` file.
Refer to the Fail2Ban documentation for more information on rule customization. You may configure additional settings like:

* Set `port = <your_ssh_port>` to specify the SSH port you are using (default is 22).
* Set `maxretry = <number_of_attempts>` to define the number of failed login attempts before an IP gets banned (recommended value: 3-5).
* Set `bantime = <ban_duration>` to specify the duration an IP remains banned (recommended value: 1 hour or more).
