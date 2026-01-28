# Git 仓库迁移指南

将本项目从原仓库迁移到新的远程仓库。

## 原仓库地址

```
git@github.com:WeTechHK/knowledge-project-test-example.git
```

## 迁移步骤

### 1. 克隆原仓库（如果本地没有）

```bash
git clone git@github.com:WeTechHK/knowledge-project-test-example.git
cd knowledge-project-test-example
```

### 2. 拉取所有分支和标签

```bash
git fetch origin --all --tags
```

### 3. 添加新的远程仓库

```bash
git remote add new-origin <新仓库地址>
```

示例：
```bash
git remote add new-origin git@github.com:your-username/new-repo.git
```

### 4. 推送所有分支到新仓库

```bash
git push new-origin --all
```

### 5. 推送所有标签到新仓库

```bash
git push new-origin --tags
```

## 迁移完成后（可选）

如果你想将默认远程仓库切换到新仓库：

```bash
# 将 origin 指向新仓库
git remote set-url origin <新仓库地址>

# 删除临时的 new-origin
git remote remove new-origin
```

## 验证

查看当前远程仓库配置：

```bash
git remote -v
```
