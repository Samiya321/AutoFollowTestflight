# GitHub Action 工作流说明

仓库包含 3 个工作流：

* `Update TestFilght Link Status`: 定时(utc时间每天3点)更新仓库内 TestFlight 链接的状态
* `Add A TestFilght Link`: 手动添加一个 TestFlight 链接
* `Del A TestFilght Link`: 手动删除一个 TestFlight 链接

## 更新仓库链接说明

### 1. 更新链接的状态

你无需手动更新状态，Github Action 会每天自动检查并更新状态。当然，你可以手动运行 `Update TestFilght Link Status` 这个 Github Action Workflow 来更新仓库内链接的状态。

### 2. 添加或删除 TestFlight 公开测试链接

你可以运行 `Add A TestFilght Link` 或 `Del A TestFilght Link` 这两个 Github Action Workflow 来添加或删除一个 TestFlight 公开测试链接。只需点击顶部的 Actions 然后在左边选择对应的 Workflow 名称，再点右边的 Run workflow 按照提示输入对应参数即可。
没有设置修改，因为感觉用不上，而且懒得弄。

### 3. 添加或删除非 TestFlight 公开测试链接（如需要填写表单申请的 TestFlight 测试）

因为没有打算将此部分链接放入数据库，所以需要添加或删除此类型链接的话，请手动修改 [`./scripts/data/signup.md`](./scripts/data/signup.md) 文件，然后手动运行一次任意工作流(推荐运行 `Update TestFilght Link Status` )即可在首页的 [`./README.md`](./README.md) 上同样更新你的修改。

### 4. 其他说明

由于本仓库内包含[二进制数据库文件](./db/sqlite3.db)，其他人拉取仓库并进行更新后请确保你在提交 PR 前同步了仓库再进行变更，避免合并 PR 时报冲突不好处理。尽量不要修改数据库文件（包括运行工作流也会修改数据库文件），仓库主在合并 __有数据库文件变更的__ PR 前也尽量先下载并检查对方变更的数据库文件是否正常（避免有人恶意破坏或修改数据库文件）。
