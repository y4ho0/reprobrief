# ReproBrief

[English](README.md) | 简体中文

ReproBrief 把维护者声明的复现命令转换成一份可供检查的错误报告摘要，
并将它与命令实际运行时的精确 Git 状态绑定。

它会记录命令参数、退出状态、受字节上限约束的 stdout/stderr、保守的
系统信息，以及命令执行前后的 Git 工作树状态。随后，ReproBrief 会对结果进行
尽力而为的脱敏，并把所有内容写入本地，由你在分享前检查。

ReproBrief 刻意保持小而明确：

- 没有账号、托管服务、遥测，运行时也不会主动访问网络；
- 不做 shell 插值——命令必须是参数数组；
- 不收集源文件、`.env`、浏览器、编辑器、聊天或提示词内容；
- 没有第三方运行时依赖；
- 不声称产物一定不含敏感信息，也不声称命令运行在沙箱中。

> [!IMPORTANT]
> `reprobrief.json` 可以要求 ReproBrief 执行程序。批准前必须检查配方，并先运行
> `reprobrief inspect`。只能运行你信任的配方。ReproBrief **不会对命令进行沙箱隔离**。
> 分享前请检查每个生成文件；脱敏只是尽力而为，不是隐私保证。

## 安装

ReproBrief 需要 CPython 3.11 或更高版本。

从已标记的 GitHub 发布版安装：

```console
python -m pip install "reprobrief @ git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
reprobrief --version
```

如果希望隔离安装，可以使用 [`pipx`](https://pipx.pypa.io/stable/)：

```console
pipx install "git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
```

发布页同时提供 wheel、源码包与 `SHA256SUMS`：
[ReproBrief v0.1.0](https://github.com/y4ho0/reprobrief/releases/tag/v0.1.0)。

## 快速开始

在发生故障的仓库中执行：

```console
reprobrief init
```

编辑生成的 `reprobrief.json`，让参数数组表达真实的复现命令：

```json
{
  "schema_version": 1,
  "commands": [
    {
      "name": "tests",
      "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"],
      "cwd": ".",
      "expected_exit_codes": [0],
      "timeout_seconds": 120,
      "max_output_bytes": 65536,
      "inherit_env": []
    }
  ]
}
```

预览将被采集的信息与解析后的参数结构：

```console
reprobrief inspect
```

终端预览会遮罩可识别的路径、环境变量值和类似凭据的参数。如果需要核对字面声明，
请直接检查配方文件。

确认预览后执行：

```console
reprobrief run
```

在非交互环境中，`--yes` 表示调用者已明确批准：

```console
reprobrief run --yes --archive
```

默认输出位于 `reprobrief-output/`；`--archive` 还会生成
`reprobrief-output.zip`。两者都不会被上传。

如果没有配方，`reprobrief run` 只会收集保守的系统和 Git 信息，不执行任何命令。

## 配方可以控制什么

每条命令支持以下字段：

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `name` | 是 | 可安全用作文件名的键，在配方中唯一 |
| `argv` | 是 | 非空的程序与参数数组；绝不能是 shell 字符串 |
| `cwd` | 否 | 仓库内已存在的目录；默认为 `.` |
| `expected_exit_codes` | 否 | 被归类为预期结果的退出码；默认为 `[0]` |
| `timeout_seconds` | 否 | `1`–`300`；默认为 `30` |
| `max_output_bytes` | 否 | **每个输出流**保留的字节数，`1024`–`1048576`；默认为 `65536` |
| `inherit_env` | 否 | 明确传递给命令的环境变量**名称** |

未知字段会被视为错误。机器可读的结构定义位于
[`docs/reprobrief.schema.json`](docs/reprobrief.schema.json)。运行时校验还会检查仓库边界、参数总大小、
不区分大小写的名称冲突以及跨平台输出文件名。

如果 `argv` 的第一项恰好是 `{python}`，ReproBrief 会将它替换为当前运行
ReproBrief 的 Python 解释器。`inspect` 会同时显示原始声明和解析后的可执行文件，
报告则记录解析后的参数向量。该标记出现在其他参数位置时会被拒绝。

子命令会收到一组最小的跨平台环境（`PATH`、临时目录变量、区域设置，以及存在时的
Windows 进程变量），再加上 `inherit_env` 中声明的名称。显式继承的值会被登记为
精确值脱敏目标，不会作为 manifest 字段写入。但程序仍可以对敏感值做变换、分割、
编码或哈希，从而超出 ReproBrief 的识别能力。应优先使用没有外部价值的测试凭据。

## 输出

```text
reprobrief-output/
├── README.md
├── manifest.json
├── report.md
└── commands/
    ├── tests.stderr.txt
    └── tests.stdout.txt
```

`manifest.json` 是带有 schema 版本的权威记录；`report.md` 是便于阅读的呈现。
大型输出流会被持续排空，以避免管道死锁，但只保留配置上限内的前缀；字节数与截断状态
会被记录。

Git 状态会在命令执行前采集一次，并在写入报告文件前再采集一次。ReproBrief 会报告
新出现和已消失的状态条目，但绝不会重置或回滚命令造成的副作用。

默认情况下，已存在的输出目录不会被替换。`--force` 只会替换带有有效
ReproBrief 标记的目录。符号链接输出目标会被拒绝。

## 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 摘要写入成功，且每条命令都是预期结果 |
| `2` | 用法或批准失败 |
| `3` | 配方或仓库输入无效 |
| `4` | 摘要已写入，但命令失败/超时，或者需要隐私审查 |
| `5` | 输出或归档错误 |
| `130` | 用户中断 |

只要输出仍能安全写入，非预期的命令结果也会生成摘要。这个失败观测通常正是维护者
需要的证据。

## 安全与隐私边界

ReproBrief 可以减少意外泄露，但不能使任意日志自动变得可以安全分享。它会对精确的仓库/
用户目录路径、显式继承的环境变量值，以及一组经过测试的高置信度凭据、邮箱和私钥形态进行脱敏。

它**不会**：

- 对配方命令进行沙箱隔离，或让它们自动变得安全；
- 发现每一种敏感信息格式或语义标识符；
- 阻止命令访问文件、凭据或网络；
- 防护恶意仓库、可执行文件、依赖或操作系统；
- 检查超出字节上限而被丢弃的命令输出；
- 上传、加密、签名或证明报告；
- 保证在所有操作系统上完整清理进程树。

在自动化工作流中采用 ReproBrief 前，请阅读中文
[安全政策](SECURITY.zh-CN.md)、[隐私与威胁模型](docs/privacy.zh-CN.md)以及英文
[设计文档](docs/design.md)。

## 演示配方

[`examples/demos`](examples/demos) 中提供了三个有明确边界的配方：

- `success.json`：预期输出和退出状态；
- `unexpected-exit.json`：真实的失败观测和退出码；
- `mutation-and-redaction.json`：显式环境变量值和工作树变更（只应在可丢弃仓库中使用）。

无需复制即可运行示例：

```console
reprobrief inspect --config examples/demos/success.json
reprobrief run --config examples/demos/success.json --yes --output demo-brief
```

## 开发

测试不依赖第三方测试框架：

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
