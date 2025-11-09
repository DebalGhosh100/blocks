#!/usr/bin/env python3
"""
SSH Log Streamer - Execute remote commands and stream logs to local file
"""

import sys
import argparse

# Import from utils package
from utils import SSHLogStreamer


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Execute remote SSH commands and stream logs to local file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ssh_log_streamer.py user@host.com password123 "ls -la" ./logs/output.log
  python ssh_log_streamer.py ssh://admin@192.168.1.100 pass "wget http://example.com/large.iso" C:\\logs\\download.log
  python ssh_log_streamer.py root@server.com secret "dd if=/dev/zero of=/tmp/test bs=1M count=1000" /var/logs/dd.log
        """
    )
    
    parser.add_argument('ssh_url', help='SSH URL (user@host or ssh://user@host:port)')
    parser.add_argument('password', help='Password for SSH authentication')
    parser.add_argument('command', help='Linux command to execute on remote machine')
    parser.add_argument('log_file', help='Destination log file path (relative or absolute)')
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Create streamer instance
    streamer = SSHLogStreamer(
        ssh_url=args.ssh_url,
        password=args.password,
        command=args.command,
        log_file=args.log_file
    )
    
    try:
        # Connect to SSH server
        if not streamer.connect():
            sys.exit(1)
        
        # Stream logs
        success = streamer.stream_logs()
        
        # Exit with appropriate status
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    finally:
        streamer.close()


if __name__ == '__main__':
    main()
