#!/usr/bin/env python3
"""
Remotely - Execute remote commands via SSH and stream logs to local file
"""

import sys
import os
import argparse

# Import from utils package
from utils import SSHLogStreamer, Colors


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Execute remote SSH commands and stream logs to local file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python remotely.py user@host.com password123 "ls -la" ./logs/output.log
  python remotely.py ssh://admin@192.168.1.100 pass "wget http://example.com/large.iso" ./logs/download.log
  python remotely.py root@server.com secret "dd if=/dev/zero of=/tmp/test bs=1M count=1000" ./logs/dd.log
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
    
    # Get the working directory from environment variable (set by blocks_executor)
    # or use current working directory as fallback
    workflow_dir = os.environ.get('BLOCKS_WORKFLOW_DIR', os.getcwd())
    
    # Create streamer instance with workflow directory context
    streamer = SSHLogStreamer(
        ssh_url=args.ssh_url,
        password=args.password,
        command=args.command,
        log_file=args.log_file,
        workflow_dir=workflow_dir
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
        print(Colors.colorize("\n\nInterrupted by user", Colors.YELLOW))
        sys.exit(130)
    except Exception as e:
        print(Colors.colorize(f"\nUnexpected error: {e}", Colors.RED))
        sys.exit(1)
    finally:
        streamer.close()


if __name__ == '__main__':
    main()
