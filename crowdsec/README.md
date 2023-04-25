# ipverse-tools-crowdsec

## crowdsec-ban-as.sh

This Bash script bans all announced networks for a given Autonomous System (AS) using Crowdsec's `cscli` command. The script fetches network ranges for both IPv4 and IPv6 and 
applies the ban for a specified duration.

### Usage

```bash
./crowdsec-ban-as.sh [--silent] <ASN> <duration>
```

- `--silent`: Optional flag to suppress the output, suitable for running as a cron job.
- `<ASN>`: Autonomous System Number, e.g. 12345.
- `<duration>`: Duration of the ban, e.g. 1h, 2d, or 1w. The format is a positive integer followed by 's' (seconds), 'm' (minutes), 'h' (hours), 'd' (days), 'w' (weeks), 'M' 
(months), or 'y' (years).

### Example

```bash
./as_network_blocker.sh --silent 12345 1d
```

This command will ban all networks announced by AS12345 for 1 day, and the `--silent` flag will suppress the output.

### Cron Job Operation

To run this script as a cron job, you can place it in the `/etc/cron.daily` directory with the `--silent` flag. Make sure to update the script path and other arguments as needed.

1. Create a new script file in `/etc/cron.daily`:

   ```
   sudo nano /etc/cron.daily/crowdsec-ban-as
   ```

2. Add the following content to the script:

   ```sh
   #!/bin/sh
   /usr/local/bin/crowdsec-ban-as.sh --silent 398324 24h01m
   ```

3. Save the file and exit the editor.

4. Make the script executable:

   ```
   sudo chmod +x /etc/cron.daily/crowdsec-ban-as
   ```

Now, the script will run daily with the specified ASN and duration.

## Requirements

- [Crowdsec](https://crowdsec.net/) and `cscli` command should be installed and configured.
- A Crowdsec Bouncer has to be up and running
- `curl` should be installed on the system.

## Notes

Please make sure to run the script with proper permissions and in an environment where `cscli` is accessible and functional.
