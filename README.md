## BLiveVote

基于blivedm的直播间投票器客户端。

### 安装

在 https://github.com/thautwarm/BLiveVote/releases 页面下载最新的发行版，解压后，按照下面的指南运行`blivevote.exe`即可。

#### 源码安装

1. `git submodule update --init --recursive`初始化`blivedm`子模块

2. 通过pip+git安装该Python包: `pip install git+https://github.com/thautwarm/BLiveVote.git`

### 使用方法

1. `blivevote --room=22637920 --pattern="投票关键词" --db 数据存储地址`

2. 在打开的UI中，输入投票选手名和投票计分起始时间，创建投票选项

3. 在直播间中，输入上述设定的投票关键词，即可为选手投票

### 使用Up主大表情投票?

如果大表情名称为“打call”, 直播间号为XXXX,则投票程序可按如下命令启动：

```
blivevote --room=XXXX --pattern="打call" --db 数据存储地址
```
