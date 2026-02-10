# Cocoon Paraphrase Examples

This directory contains pre-built paraphrase strings ready to use.

## Available Examples

### 1. Hello World (`hello-world.txt`)

The simplest possible Cocoon workflow.

**Deploy:**
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/examples/hello-world.txt | base64 -d | bash
```

**Or manually:**
```bash
echo "IyEvYmluL2Jhc2gKCiMgQ29jb29uIFdvcmtmbG93IFN0cnVjdHVyZSBTZXR1cCBTY3JpcHQKIyBHZW5lcmF0ZWQgYnkgQ29jb29uIFBhcmFwaHJhc2UKCnNldCAtZSAgIyBFeGl0IG9uIGFueSBlcnJvcgoKZWNobyAiQ3JlYXRpbmcgd29ya2Zsb3cgc3RydWN0dXJlLi4uIgplY2hvICIiCgpjYXQgPiAibWFpbi55YW1sIiA8PCAnRU9GJwpibG9ja3M6CiAgLSBydW46ICdlY2hvICJIZWxsbywgQ29jb29uISInCkVPRgoKZWNobyAiIgplY2hvICLinJMgV29ya2Zsb3cgc3RydWN0dXJlIGNyZWF0ZWQgc3VjY2Vzc2Z1bGx5ISIKZWNobyAiUnVuICdjb2Nvb24gbWFpbi55YW1sJyB0byBleGVjdXRlIHlvdXIgd29ya2Zsb3cuIgo=" | base64 -d | bash
```

**Creates:**
- `main.yaml` - Simple hello world workflow

---

### 2. Basic Sequential (`basic-sequential.txt`)

A workflow with multiple sequential steps and a parameters directory.

**Deploy:**
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/examples/basic-sequential.txt | base64 -d | bash
```

**Or manually:**
```bash
echo "IyEvYmluL2Jhc2gKCiMgQ29jb29uIFdvcmtmbG93IFN0cnVjdHVyZSBTZXR1cCBTY3JpcHQKIyBHZW5lcmF0ZWQgYnkgQ29jb29uIFBhcmFwaHJhc2UKCnNldCAtZSAgIyBFeGl0IG9uIGFueSBlcnJvcgoKZWNobyAiQ3JlYXRpbmcgd29ya2Zsb3cgc3RydWN0dXJlLi4uIgplY2hvICIiCgpjYXQgPiAibWFpbi55YW1sIiA8PCAnRU9GJwpibG9ja3M6CiAgLSBydW46ICdlY2hvICJTdGVwIDE6IEhlbGxvIGZyb20gQ29jb29uISInCiAgLSBydW46ICdlY2hvICJTdGVwIDI6IEN1cnJlbnQgZGlyZWN0b3J5OiAkKHB3ZCkiJwogIC0gcnVuOiAnZWNobyAiU3RlcCAzOiBMaXN0IGZpbGVzIicKICAtIHJ1bjogJ2xzIC1sYScKRU9GCm1rZGlyIC1wICJwYXJhbWV0ZXJzIgpjYXQgPiAicGFyYW1ldGVycy9jb25maWcueWFtbCIgPDwgJ0VPRicKZW52aXJvbm1lbnQ6IGRldmVsb3BtZW50CmRlYnVnOiB0cnVlCnRpbWVvdXQ6IDMwCnNlcnZlcnM6CiAgLSBuYW1lOiBzZXJ2ZXIxCiAgICBpcDogMTkyLjE2OC4xLjEwCiAgLSBuYW1lOiBzZXJ2ZXIyCiAgICBpcDogMTkyLjE2OC4xLjExCkVPRgoKZWNobyAiIgplY2hvICLinJMgV29ya2Zsb3cgc3RydWN0dXJlIGNyZWF0ZWQgc3VjY2Vzc2Z1bGx5ISIKZWNobyAiUnVuICdjb2Nvb24gbWFpbi55YW1sJyB0byBleGVjdXRlIHlvdXIgd29ya2Zsb3cuIgo=" | base64 -d | bash
```

**Creates:**
- `main.yaml` - Sequential workflow with 4 steps
- `parameters/config.yaml` - Configuration file with environment settings

---

## Creating Your Own Paraphrases

1. **Create your workflow:**
   ```bash
   mkdir my-workflow
   cd my-workflow
   # Create your YAML files
   ```

2. **Generate paraphrase:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/paraphrase.sh | bash -s .
   ```

3. **Save the output:**
   Copy the base64 string and save it to a `.txt` file

4. **Share it:**
   - Commit to your repository
   - Share via URL
   - Include in documentation
   - Send via chat/email

---

## Tips

- **Test before sharing**: Always decode and test your paraphrase in a clean directory
- **Version control**: Save paraphrases with version numbers or git commits
- **Documentation**: Include a comment in your paraphrase about what it creates
- **Security**: Never include sensitive data (passwords, tokens) in paraphrases

---

## Quick Test

Try the hello-world example right now:

```bash
mkdir test-paraphrase && cd test-paraphrase
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/examples/hello-world.txt | base64 -d | bash
ls -la
cat main.yaml
```
