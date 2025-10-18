# DES配方推荐系统 - 前端

DES (Deep Eutectic Solvent) 配方推荐系统的 Web 前端应用，基于 React + TypeScript + Ant Design 构建。

## 技术栈

- **框架**: React 18
- **构建工具**: Vite 6
- **语言**: TypeScript 5
- **UI 组件库**: Ant Design 5
- **HTTP 客户端**: Axios
- **路由**: React Router DOM 7
- **日期处理**: Day.js
- **图标**: @ant-design/icons

## 项目结构

```
src/web_frontend/
├── src/
│   ├── components/         # 可复用组件
│   ├── pages/              # 页面组件
│   │   ├── TaskSubmissionPage.tsx       # 任务提交
│   │   ├── RecommendationListPage.tsx   # 推荐列表
│   │   ├── RecommendationDetailPage.tsx # 推荐详情
│   │   ├── FeedbackPage.tsx             # 反馈提交
│   │   └── StatisticsPage.tsx           # 统计仪表板
│   ├── services/           # API 服务
│   │   ├── api.ts                      # Axios 配置
│   │   ├── taskService.ts              # 任务API
│   │   ├── recommendationService.ts    # 推荐API
│   │   ├── feedbackService.ts          # 反馈API
│   │   ├── statisticsService.ts        # 统计API
│   │   └── index.ts                    # 统一导出
│   ├── types/              # TypeScript 类型定义
│   │   └── index.ts
│   ├── App.tsx             # 主应用组件
│   └── main.tsx            # 应用入口
├── package.json
├── vite.config.ts
├── tsconfig.json
├── .env.example            # 环境变量模板
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd src/web_frontend
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将运行在 http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 5. 预览生产构建

```bash
npm run preview
```

## 功能模块

### 1. 任务提交 (Task Submission)

**路由**: `/`

**功能**:
- 提交DES配方需求（任务描述、目标材料、目标温度、约束条件）
- 实时获取系统推荐的DES配方列表
- 查看推荐详情和提交实验反馈

### 2. 推荐列表 (Recommendation List)

**路由**: `/recommendations`

**功能**:
- 查看所有DES配方推荐
- 按状态筛选（待实验/已完成/已取消）
- 按材料筛选
- 分页展示

### 3. 推荐详情 (Recommendation Detail)

**路由**: `/recommendations/:id`

**功能**:
- 查看推荐的完整信息（组分、推理过程、置信度、参考文献、实验结果等）

### 4. 反馈提交 (Feedback Submission)

**路由**: `/feedback/:id`

**功能**:
- 提交实验结果（液体形成、溶解度、温度、其他性质、备注）

### 5. 统计仪表板 (Statistics Dashboard)

**路由**: `/statistics`

**功能**:
- 系统性能概览（总推荐数、待实验、已完成、平均性能得分等）
- 按材料分布、按状态分布
- 性能趋势分析（支持日期范围筛选）
- 最佳配方 Top 10

## API 集成

所有API请求通过 Axios 实例统一管理，配置在 `src/services/api.ts`。

**Base URL**: 从环境变量 `VITE_API_BASE_URL` 读取（默认 `http://localhost:8000`）

## 浏览器兼容性

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 故障排除

### API请求失败（CORS错误）

确保后端启用了CORS，并在配置中包含前端地址：

```python
# src/web_backend/config.py
cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

### 环境变量未生效

1. 确认 `.env` 文件在项目根目录
2. 环境变量名必须以 `VITE_` 开头
3. 修改 `.env` 后需要重启开发服务器

---

**最后更新**: 2025-10-16
**版本**: v1.0.0 (MVP Complete ✅)
