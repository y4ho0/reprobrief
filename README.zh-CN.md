# ReproBrief

[English](README.md) | 简体中文

当有人说“这个项目运行失败”时，ReproBrief 可以帮助他在本地生成一份可检查的
问题复现包，而不是只发一张截图或一小段错误信息。

它适合需要完整问题上下文的维护者，也适合需要提供这些信息的贡献者和用户。
复现包会展示实际运行的命令、有限长度的输出、基础环境信息以及失败当时的仓库状态。

复现包保留在用户电脑上；ReproBrief 不会自动上传。它只会运行用户可先检查、再批准的
JSON 配方中声明的程序。ReproBrief **不是沙箱**，分享前必须检查每个生成文件。

## 你可能遇到过这种情况吗？

用户报告项目失败，但只附上一张错误截图。维护者还得继续追问：

- 你实际运行了什么命令？
- 你用的是哪个 Python 版本和操作系统？
- 命令失败前输出了什么？
- 当时检出的是哪个 Git 修订版？
- 命令或本地工作区里是否存在未提交变更？

这种往返沟通会拖慢定位，关键上下文也很容易丢失。ReproBrief 每次都收集同一组
有明确边界的信息，并将它们放进一份由报告者先检查、再交给维护者的复现包。
这是产品的目标工作流，不代表已获得外部用户验证。

## ReproBrief 会做什么

```text
经过检查的复现命令
→ 一次经批准的本地执行
→ 可检查的报告目录和可选 ZIP
```

ReproBrief 会：

- 先显示执行计划，获得批准后才运行命令；
- 记录解析后的命令参数、退出码、耗时和结果分类；
- 在持续读取两个输出流的同时，只保留可配置长度的标准输出和标准错误
  （`stdout` 和 `stderr`）；
- 记录保守的操作系统、Python、ReproBrief 和 Git 信息；
- 对比命令执行前后的 Git 工作区状态；
- 尽力遮罩可识别的路径、显式继承的环境变量值和部分高置信度敏感形态；
- 生成本地的人类可读报告、结构化记录、命令输出文件和可选 ZIP。

它不收集源文件、`.env` 文件、浏览器/编辑器/聊天内容或提示词。ReproBrief 自身
不会发起网络请求，但获得批准的子命令可以独立读取文件、修改仓库或使用网络。

## 先看结果

使用 `--archive` 成功运行后，仓库中会出现：

```text
reprobrief-output/
├── README.md
├── manifest.json
├── report.md
└── commands/
    ├── tests.stderr.txt
    └── tests.stdout.txt
reprobrief-output.zip
```

- `report.md` 是给人阅读的问题摘要。
- `manifest.json` 是带有 schema 版本的结构化记录，便于工具处理或深入检查。
- `commands/` 包含每条命令保留下来的标准输出和标准错误。
- 生成的 `README.md` 会在证据旁再次提醒用户检查隐私和安全风险。
- `reprobrief-output.zip` 包含同一组生成文件。用户检查每个文件后，可以自行选择
  将它附加到 issue 或通过自己控制的渠道发送。ReproBrief 绝不会自动发送。

命令非预期退出或超时时，仍可能生成这份复现包。失败观测通常正是维护者需要的证据。

## 安装

ReproBrief 需要 CPython 3.11 或更高版本。它尚未发布到 PyPI；请直接安装已验证的
GitHub `v0.1.0` 发布版：

```console
python -m pip install "reprobrief @ git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
reprobrief --version
```

预期版本输出：

```text
reprobrief 0.1.0
```

如果希望隔离安装，可以使用 [`pipx`](https://pipx.pypa.io/stable/)：

```console
pipx install "git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
```

[v0.1.0 Release](https://github.com/y4ho0/reprobrief/releases/tag/v0.1.0)
还提供 wheel、源码包与 `SHA256SUMS`。

## 快速开始

在发生故障的仓库中完成以下四步。

1. **创建配方文件。** 这会写入 `reprobrief.json`，但不会覆盖已存在的文件。

   ```console
   reprobrief init
   ```

2. **填写真实的复现命令。** 编辑 `reprobrief.json`。下面是使用 Python 内置测试运行器的
   最小有效配置；请把 `argv` 替换为实际能够复现问题的命令。

   ```json
   {
     "schema_version": 1,
     "commands": [
       {
         "name": "tests",
         "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"]
       }
     ]
   }
   ```

3. **只预览，不执行。** 确认解析后的程序、参数、工作目录、超时时间、输出上限以及
   将被收集的信息。

   ```console
   reprobrief inspect
   ```

> [!IMPORTANT]
> 下一步会执行 `reprobrief.json` 中声明的程序。请先检查配方，只运行你信任的命令。
> ReproBrief **不会对命令进行沙箱隔离**。分享前检查每个生成文件；遮罩只是
> 尽力而为，不是隐私保证。

4. **批准命令并生成复现包。** `--yes` 记录明确的非交互批准；`--archive` 同时创建 ZIP。

   ```console
   reprobrief run --yes --archive
   ```

终端应该显示两行以下列内容结尾的 `Wrote` 信息：

```text
.../reprobrief-output
.../reprobrief-output.zip
```

先打开 `reprobrief-output/report.md`，然后检查 `manifest.json` 和 `commands/` 中的每个文件。
不会上传任何内容。如果希望使用交互式批准，可改用 `reprobrief run`，并仅在检查计划后回答 `y`。

## 适合使用 ReproBrief

- 问题报告缺少精确命令、完整但有上限的日志，或基础环境信息。
- 维护者需要在同一次失败观测中看到 Git 修订版和执行前后的工作区状态。
- 报告者希望先在本地检查一份完整复现包，再自行决定是否分享。
- 项目不希望诊断证据被自动上传到第三方服务。
- 仓库可以提供一份精简且受信任的复现配方。

## 不适合使用 ReproBrief

- 仓库或命令不受信任，必须运行在真正的安全沙箱中。
- 要求保证报告绝不包含秘密或私有信息。
- 工作流需要自动上传、托管存储或远程执行。
- 目标是完整跟踪文件访问、系统调用或网络流量。
- 目标是自动诊断、修复，或忠实重现一台 CI 机器。

如果这些才是真正需求，应使用沙箱、跟踪工具、托管支持系统或项目专用诊断工具。

## 它会创建或修改什么

- `reprobrief init` 只会创建指定的配方文件，并拒绝覆盖已存在的文件。
- `reprobrief run` 默认创建 `reprobrief-output/`；`--archive` 还会创建
  `reprobrief-output.zip`。
- 默认不会替换已存在的输出。`--force` 只会替换 ReproBrief 能够识别为自身产物的目录
  或归档；符号链接输出目标会被拒绝。
- ReproBrief 不会重置或撤销子命令的副作用。获得批准的命令可以用当前用户的权限修改文件、
  运行其他程序或使用网络。
- ReproBrief 没有账号、服务器、后台进程或隐藏的远程副本。不再需要时，可删除生成的目录、
  ZIP 和配方。通过 pip 安装的包可使用 `python -m pip uninstall reprobrief` 卸载。

如果没有配方，`reprobrief run` 只会收集保守的系统和 Git 信息，不执行任何已声明命令。

## 安全与隐私

ReproBrief 可以减少一部分意外泄露，但不能让任意日志自动变得安全。它会遮罩精确的仓库/
用户目录路径、显式继承的环境变量值，以及一组经过测试的高置信度凭据、邮箱、URL 凭据和私钥形态。

它**不会**：

- 对配方命令进行沙箱隔离，或让它们自动变得安全；
- 发现每一种秘密格式或语义标识符；
- 阻止获得批准的命令访问文件、凭据或网络；
- 防护恶意仓库、可执行文件、依赖或操作系统；
- 检查超出配置字节上限而被丢弃的命令输出；
- 上传、加密、签名或证明报告；
- 保证在所有操作系统上完整清理进程树。

在自动化工作流中使用 ReproBrief 前，请阅读完整的中文
[安全政策](SECURITY.zh-CN.md)、[隐私与威胁模型](docs/privacy.zh-CN.md)和英文
[设计文档](docs/design.md)。

## 配置参考

JSON 配置文件中的每条命令支持以下字段：

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `name` | 是 | 可安全用作文件名的键，在配方中唯一 |
| `argv` | 是 | 非空的程序与参数数组；绝不能是 shell 字符串 |
| `cwd` | 否 | 仓库内已存在的目录；默认为 `.` |
| `expected_exit_codes` | 否 | 被分类为预期结果的退出码；默认为 `[0]` |
| `timeout_seconds` | 否 | `1`–`300`；默认为 `30` |
| `max_output_bytes` | 否 | **每个输出流**保留的字节数，`1024`–`1048576`；默认为 `65536` |
| `inherit_env` | 否 | 明确传递给命令的环境变量**名称** |

未知字段会被视为错误。机器可读的结构定义位于
[`docs/reprobrief.schema.json`](docs/reprobrief.schema.json)。运行时校验还会检查仓库边界、参数总大小、
不区分大小写的名称冲突和跨平台输出文件名。

如果 `argv` 的第一项恰好是 `{python}`，ReproBrief 会将它替换为当前运行
ReproBrief 的 Python 解释器。`inspect` 会同时显示原始声明和解析后的可执行文件。
该标记出现在其他参数位置时会被拒绝。

子命令会收到一组最小的跨平台环境（`PATH`、临时目录变量、区域设置，以及存在时的
Windows 进程变量），再加上 `inherit_env` 中声明的名称。显式继承的值会在持久化前登记为
精确替换目标，但程序可以变换、分割、编码或哈希某个值，从而超出 ReproBrief 的识别能力。
应优先使用没有外部价值的可丢弃测试凭据。

命令输出会被持续读取以避免管道死锁，但只保留每个输出流中受配置上限约束的前缀。
字节数和截断状态会被记录。Git 状态会在执行前采集一次，并在写入报告文件前再采集一次。

## 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 复现包写入成功，且每条命令都是预期结果 |
| `2` | 用法或批准失败 |
| `3` | 配方或仓库输入无效 |
| `4` | 复现包已写入，但命令失败/超时，或需要隐私审查 |
| `5` | 输出或归档错误 |
| `130` | 用户中断 |

只要输出仍能写入，命令的非预期结果也会生成复现包。

## 演示配方

[`examples/demos`](examples/demos) 中提供了三个有明确边界的配方：

- `success.json`：预期输出和退出状态；
- `unexpected-exit.json`：真实失败观测和退出码；
- `mutation-and-redaction.json`：显式环境变量值和工作区变更（只应在可丢弃仓库中使用）。

无需复制即可运行安全的成功示例：

```console
reprobrief inspect --config examples/demos/success.json
reprobrief run --config examples/demos/success.json --yes --output demo-brief
```

## 开发与贡献

测试不需要第三方测试框架：

```console
PYTHONPATH=src python -m unittest discover -s tests -v
```

从本地检出安装并运行冒烟路径：

```console
python -m pip install --no-deps .
reprobrief --version
reprobrief inspect --config examples/demos/success.json
```

质量与变更流程见英文 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

Apache-2.0，详见 [LICENSE](LICENSE)。
