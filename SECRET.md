使用SOPS加密管理的具体步骤分为准备阶段和使用阶段,以下是详细流程:

## 准备阶段

### 安装工具

首先需要安装SOPS和加密工具 。根据操作系统不同: [semanticscholar](https://www.semanticscholar.org/paper/2f0de64ed0cf1d791507372b901bbbfd73e3495c)

- **macOS**: `brew install sops gnupg` 或 `brew install age sops`
- **Ubuntu/Debian**: `sudo apt install sops gnupg2`
- **Arch Linux**: `sudo pacman -S sops gnupg`

### 生成密钥对

可以选择使用GPG或Age加密方式 。 [ieeexplore.ieee](https://ieeexplore.ieee.org/document/11058500/)

**使用Age(推荐)**:
```bash
age-keygen -o age.agekey
```
这会生成一个包含私钥和公钥的文件 。公钥以`age1`开头,显示在文件的注释行中 。 [deyan7](https://deyan7.de/sops-secrets-operations-kubernetes-operator-secure-your-sensitive-data-while-maintaining-ease-of-use/)

**使用GPG**:
```bash
gpg --batch --full-generate-key <<EOF
Key-Type: 1
Key-Length: 4096
Subkey-Type: 1
Name-Real: cluster.local
EOF
```
记录生成的密钥指纹(fingerprint) 。 [semanticscholar](https://www.semanticscholar.org/paper/2f0de64ed0cf1d791507372b901bbbfd73e3495c)

### 将私钥存储到集群

创建Kubernetes Secret保存私钥: [ieeexplore.ieee](https://ieeexplore.ieee.org/document/11058500/)

**Age方式**:
```bash
cat age.agekey | kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=age.agekey=/dev/stdin
```

**GPG方式**:
```bash
gpg --export-secret-keys --armor "密钥指纹" | kubectl create secret generic sops-gpg \
  --namespace=flux-system \
  --from-file=sops.asc=/dev/stdin
```

### 配置FluxCD解密

修改Flux的Kustomization配置,启用SOPS解密功能: [semanticscholar](https://www.semanticscholar.org/paper/2f0de64ed0cf1d791507372b901bbbfd73e3495c)

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: flux-system
  namespace: flux-system
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age  # 或 sops-gpg
```

## 使用阶段

### 创建SOPS配置文件

在Git仓库根目录创建`.sops.yaml`配置文件: [ieeexplore.ieee](https://ieeexplore.ieee.org/document/11058500/)

```yaml
creation_rules:
  - path_regex: .*.yaml
    encrypted_regex: ^(data|stringData)$
    age: age1你的公钥  # 或使用 pgp: GPG密钥指纹
```

这个配置指定只加密YAML文件中的`data`和`stringData`字段 。 [semanticscholar](https://www.semanticscholar.org/paper/2f0de64ed0cf1d791507372b901bbbfd73e3495c)

### 生成并加密Secret

先用kubectl生成Secret的YAML文件: [fluxcd](https://fluxcd.io/flux/guides/mozilla-sops/)

```bash
kubectl create secret generic basic-auth \
  --from-literal=user=admin \
  --from-literal=password=change-me \
  --dry-run=client -o yaml > basic-auth.yaml
```

然后使用SOPS加密: [fluxcd](https://fluxcd.io/flux/guides/mozilla-sops/)

```bash
# 使用Age
SOPS_AGE_KEY_FILE=age.agekey sops --encrypt --in-place basic-auth.yaml

# 使用GPG
sops --encrypt --in-place basic-auth.yaml
```

### 提交到Git仓库

加密后的Secret文件可以安全地提交到Git仓库 。FluxCD会自动检测变化,使用集群中的私钥解密并应用到Kubernetes 。 [fluxcd](https://fluxcd.io/flux/guides/mozilla-sops/)

### 编辑已加密的Secret

如需修改加密的Secret: [deyan7](https://deyan7.de/sops-secrets-operations-kubernetes-operator-secure-your-sensitive-data-while-maintaining-ease-of-use/)

```bash
# 设置私钥文件路径
export SOPS_AGE_KEY_FILE=./age.agekey

# 直接编辑(SOPS会自动解密和重新加密)
sops basic-auth.yaml
```

这种方式确保敏感信息不会以明文形式出现在Git仓库中,同时保持了GitOps的声明式配置管理优势 。 [ieeexplore.ieee](https://ieeexplore.ieee.org/document/11058500/)