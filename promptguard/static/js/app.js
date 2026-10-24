/* PromptGuard frontend behavior: i18n, theme, responsive navigation, scan form, and tables. */
document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  const LANGUAGE_KEY = "promptguard-language";
  const THEME_KEY = "promptguard-theme";
  const zh = {
    "brand.subtitle": "AI 安全工作空间",
    "nav.workspace": "工作空间",
    "nav.resources": "资源",
    "nav.report": "扫描报告",
    "nav.dashboard": "仪表盘",
    "nav.scans": "扫描记录",
    "nav.probes": "测试探针",
    "nav.policies": "检测策略",
    "nav.knowledge": "知识库",
    "nav.integrations": "集成",
    "nav.settings": "设置",
    "nav.open": "打开导航菜单",
    "page.report": "扫描报告",
    "page.dashboard": "仪表盘",
    "page.scans": "扫描记录",
    "page.probes": "测试探针",
    "page.policies": "检测策略",
    "page.knowledge": "知识库",
    "page.integrations": "集成",
    "page.settings": "设置",
    "workspace.name": "默认工作空间",
    "workspace.mode": "本地分析模式",
    "status.local": "本地引擎已就绪",
    "status.private": "提示内容保留在本应用中",
    "status.online": "本地引擎运行中",
    "status.ready": "可以开始扫描",
    "language.label": "界面语言",
    "theme.toggle": "切换主题",
    "footer.note": "基于启发式规则的提示注入与有害内容检测",
    "footer.disclaimer": "仅用于学习与评估，不构成安全保证",
    "actions.export": "导出报告",
    "actions.exportCsv": "导出 CSV",
    "actions.exportJson": "导出 JSON",
    "actions.clear": "清空",
    "metrics.total": "扫描总数",
    "metrics.totalFoot": "本会话中的扫描次数",
    "metrics.passed": "通过",
    "metrics.passedFoot": "提示注入风险较低",
    "metrics.failed": "已标记",
    "metrics.failedFoot": "中风险或高风险",
    "metrics.critical": "有害内容警告",
    "metrics.criticalFoot": "独立内容警告",
    "metrics.highRisk": "高风险",
    "metrics.average": "平均分数",
    "report.eyebrow": "安全评估",
    "report.title": "扫描报告",
    "report.subtitle": "检查提示中是否存在注入模式或潜在有害意图。",
    "report.timestamp": "最近一次本地分析",
    "report.model": "模型：本地规则引擎",
    "report.framework": "框架：参考 OWASP LLM Top 10 概念",
    "report.securityScore": "安全评分",
    "report.scoreTooltip": "启发式指标，不是概率",
    "report.risk": "风险",
    "report.scoreDescription": "运行扫描后即可查看加权信号分数和相关证据。",
    "report.scoreHelp": "分数如何计算？",
    "scanner.eyebrow": "提示分析",
    "scanner.title": "分析提示",
    "scanner.subtitle": "粘贴文本，检查提示注入模式和有害意图。",
    "scanner.inputLabel": "输入文本",
    "scanner.maxLength": "最多 10,000 个字符",
    "scanner.placeholder": "粘贴要分析的提示……",
    "scanner.privacyNote": "请勿粘贴真实密码、API 密钥或私人数据。",
    "scanner.trySample": "试用示例",
    "scanner.sampleSafe": "普通提示",
    "scanner.sampleInjection": "注入示例",
    "scanner.sampleHarmful": "有害意图",
    "scanner.localNote": "分析在本地运行",
    "scanner.run": "运行安全扫描",
    "scanner.loading": "正在本地分析……",
    "harm.warning": "警告：此提示可能包含有害或危险内容。",
    "harm.description": "此警告独立于提示注入检测。请仔细审查请求；该警告本身并不能证明用户的真实意图。",
    "harm.flagged": "内容已标记",
    "harm.noWarning": "未检测到明确的有害意图模式。这并不保证内容一定安全。",
    "findings.eyebrow": "扫描证据",
    "findings.title": "检测发现",
    "findings.subtitle": "显示最近一次扫描中匹配的规则及其说明。",
    "findings.matches": "条匹配",
    "findings.matched": "已匹配",
    "findings.none": "没有匹配已配置的提示注入规则",
    "findings.noneDesc": "注入检测器没有发现明显的规则匹配。如上方存在有害内容警告，请单独查看。",
    "findings.awaiting": "扫描证据将在此处显示",
    "findings.awaitingDesc": "提交上方的提示后，即可查看匹配规则、类别和说明。",
    "findings.disclaimer": "注入分数是加权启发式指标，不是恶意概率，也不能保证内容安全。",
    "table.rule": "规则 / 探针",
    "table.category": "类别",
    "table.severity": "信号",
    "table.verdict": "结果",
    "table.evidence": "证据说明",
    "table.prompt": "输入预览",
    "table.time": "时间",
    "table.risk": "风险级别",
    "table.score": "分数",
    "table.rules": "匹配规则数",
    "table.contentAlert": "内容警告",
    "table.hits": "命中次数",
    "recommendations.eyebrow": "建议步骤",
    "recommendations.title": "优化建议",
    "recommendations.subtitle": "通过以下措施加强提示和工具的处理方式。",
    "recommendations.one": "将文档和检索段落视为不可信输入。",
    "recommendations.two": "执行敏感工具操作前要求明确授权。",
    "recommendations.three": "避免将密钥放入模型上下文，并在日志中进行脱敏。",
    "recommendations.four": "测试多语言、编码混淆和多步骤注入尝试。",
    "recommendations.five": "将有害内容警告与提示注入发现分开审查。",
    "recommendations.view": "查看检测策略",
    "details.eyebrow": "运行环境",
    "details.title": "扫描详情",
    "details.framework": "框架",
    "details.engine": "引擎",
    "details.localEngine": "本地启发式检测",
    "details.provider": "提供方",
    "details.local": "本地 / 离线",
    "details.maxInput": "最大输入",
    "details.detectors": "检测器",
    "details.detectorList": "注入检测 + 有害内容",
    "details.privacy": "不会调用外部 AI API。",
    "risk.eyebrow": "评分指南",
    "risk.title": "风险级别",
    "risk.low": "低风险",
    "risk.medium": "中风险",
    "risk.high": "高风险",
    "risk.note": "有害内容警告独立显示，不会改变提示注入分数。",
    "history.eyebrow": "活动记录",
    "history.title": "最近扫描",
    "history.subtitle": "当前浏览器会话中保留的最近记录。",
    "history.viewAll": "查看全部记录",
    "history.empty": "尚无扫描记录。完成首次分析后，结果会显示在这里。",
    "dashboard.eyebrow": "分析概览",
    "dashboard.subtitle": "清晰查看最近扫描活动、风险分布和匹配规则。",
    "dashboard.rangeLabel": "时间范围",
    "dashboard.today": "最近 24 小时",
    "dashboard.week": "最近 7 天",
    "dashboard.month": "最近 30 天",
    "dashboard.all": "全部近期记录",
    "dashboard.sessionNote": "分析数据来自本地数据库中按工作区保存的扫描记录。",
    "dashboard.sampleData": "加载示例数据",
    "dashboard.periodTotal": "所选时间段的扫描数",
    "dashboard.flaggedFoot": "中风险或高风险提示注入",
    "dashboard.highFoot": "所选时间段的高风险扫描",
    "dashboard.averageFoot": "启发式平均分数 / 100",
    "dashboard.distributionEyebrow": "风险概览",
    "dashboard.distributionTitle": "风险分布",
    "dashboard.distributionDesc": "最近的提示被注入检测器分类的情况。",
    "dashboard.analyzed": "条提示已分析",
    "dashboard.empty": "此时间段暂无扫描数据。",
    "dashboard.rulesEyebrow": "检测信号",
    "dashboard.rulesTitle": "最常匹配的规则",
    "dashboard.rulesDesc": "保留的扫描记录中最常命中的规则。",
    "dashboard.frequency": "频率",
    "dashboard.noRules": "此时间段没有匹配提示注入规则。",
    "dashboard.categoriesEyebrow": "信号分布",
    "dashboard.categoriesTitle": "检测类别",
    "dashboard.categoriesDesc": "气泡大小表示该类别的匹配次数。",
    "dashboard.filterLabel": "筛选气泡类别",
    "dashboard.filterAll": "全部",
    "dashboard.noCategories": "此筛选条件下没有类别匹配。",
    "dashboard.bubbleNote": "类别统计来自提示注入发现，不包含独立的有害内容警告。",
    "scans.eyebrow": "扫描历史",
    "scans.subtitle": "搜索最近的分析记录，并导出副本用于项目报告。",
    "scans.searchPlaceholder": "搜索提示预览或风险级别……",
    "scans.filterLabel": "按风险筛选",
    "scans.allRisk": "全部风险级别",
    "scans.harmfulOnly": "有害内容警告",
    "scans.records": "条记录",
    "scans.harmfulYes": "警告",
    "scans.noMatch": "没有符合筛选条件的扫描记录。",
    "scans.emptyTitle": "暂无扫描历史",
    "scans.emptyDesc": "请在扫描报告页面运行扫描，最近记录将显示在这里。",
    "scans.goScanner": "打开扫描器",
    "scans.retention": "为保护隐私，此原型只在浏览器会话中保留有限数量的近期记录。",
    "probes.eyebrow": "测试库",
    "probes.subtitle": "使用可复用的攻击和普通提示测试当前本地检测器。",
    "probes.localOnly": "仅本地测试",
    "probes.noteTitle": "评估说明",
    "probes.noteText": "这些是测试输入，并不代表检测器能够捕获所有技术。请结合标注数据集检查漏报和误报。",
    "probes.run": "运行此探针",
    "policies.eyebrow": "检测配置",
    "policies.subtitle": "查看本地模式检测器、结构化规则和风险阈值。",
    "policies.totalRules": "条启用规则",
    "policies.lowText": "低于 {{ medium_threshold }} 分。",
    "policies.mediumText": "分数从 {{ medium_threshold }} 到 {{ high_threshold - 1 }}。",
    "policies.highText": "分数达到 {{ high_threshold }} 或更高。",
    "policies.patternEyebrow": "正则模式",
    "policies.patternTitle": "模式检测规则",
    "policies.patternDesc": "内置规则会检查经过规范化的文本，识别常见提示注入信号。",
    "policies.structuredEyebrow": "多信号规则",
    "policies.structuredTitle": "结构化规则",
    "policies.structuredDesc": "rules.json 中的规则会组合检查同时出现的词语。",
    "policies.requiredTerms": "个必需词",
    "policies.enabled": "已启用",
    "policies.limitTitle": "启发式检测的局限",
    "policies.limitText": "规则依赖已配置的模式和词语，可能漏掉新攻击，也可能误报正常的教学文本。请先使用开发集测试规则变更，再使用留出集评估。",
    "knowledge.eyebrow": "参考资料",
    "knowledge.subtitle": "了解 PromptGuard 的检测内容、评分方式和能力边界。",
    "knowledge.injectionTitle": "什么是提示注入？",
    "knowledge.injectionText": "提示注入是试图让 AI 系统将不可信文本当作指令，覆盖原本任务、泄露隐藏上下文或执行未经授权操作的行为。",
    "knowledge.injectionOne": "直接覆盖指令和越狱措辞",
    "knowledge.injectionTwo": "文档或检索内容中的隐藏指令",
    "knowledge.injectionThree": "尝试泄露提示、密钥或私人上下文",
    "knowledge.harmTitle": "有害内容警告",
    "knowledge.harmText": "独立的模式检测器会检查看似寻求暴力、危险装置、投毒、非法活动或自伤帮助的请求。",
    "knowledge.harmNote": "该警告不会改变提示注入分数。模式匹配可能无法理解完整语境，也不能判断个人真实意图。",
    "knowledge.scoreTitle": "分数如何计算",
    "knowledge.scoreText": "每个匹配项会贡献配置的权重。总分最高为 100，并映射到低、中、高风险区间。",
    "knowledge.safeTitle": "安全的评估实践",
    "knowledge.safeText": "使用合成提示，不要将密钥放入测试数据，并同时检查误报和漏报。",
    "knowledge.safeOne": "使用开发集调整规则",
    "knowledge.safeTwo": "将留出集与调参过程分开",
    "knowledge.safeThree": "不要只报告准确率，还应报告精确率、召回率和 F1",
    "knowledge.workflowEyebrow": "工作流程",
    "knowledge.workflowTitle": "建议的审查流程",
    "knowledge.stepOneTitle": "扫描",
    "knowledge.stepOneText": "通过本地扫描器提交测试提示。",
    "knowledge.stepTwoTitle": "检查",
    "knowledge.stepTwoText": "查看匹配规则和独立的有害内容警告。",
    "knowledge.stepThreeTitle": "评估",
    "knowledge.stepThreeText": "使用多个数据集，将预测标签与真实标签进行比较。",
    "knowledge.stepFourTitle": "改进",
    "knowledge.stepFourText": "添加回归测试，并在留出样例上衡量改动效果。",
    "integrations.eyebrow": "连接服务",
    "integrations.subtitle": "PromptGuard 当前在本地运行，不会将提示发送到外部服务。",
    "integrations.localStatus": "仅本地运行",
    "integrations.privacyTitle": "默认保护隐私",
    "integrations.privacyText": "当前未配置外部 AI API。下方状态卡介绍项目当前能力，并不表示已连接第三方账户。",
    "integrations.localEngine": "PromptGuard 本地引擎",
    "integrations.localDesc": "模式匹配、结构化规则、风险评分和有害内容警告。",
    "integrations.active": "运行中",
    "integrations.githubDesc": "可使用 GitHub 仓库进行版本管理和 CI。此应用未启用 GitHub API 集成。",
    "integrations.notConnected": "未连接",
    "integrations.externalAi": "外部 AI 服务商",
    "integrations.aiDesc": "当前检测不需要外部模型，提示不会发送到外部模型。",
    "integrations.disabled": "已禁用",
    "integrations.datasets": "本地 JSON 数据集",
    "integrations.datasetsDesc": "标注的攻击和正常示例保存在项目的数据目录中。",
    "integrations.available": "本地可用",
    "settings.eyebrow": "偏好设置",
    "settings.subtitle": "自定义工作空间，并管理本地扫描会话。",
    "settings.appearanceEyebrow": "显示",
    "settings.appearanceTitle": "外观",
    "settings.appearanceDesc": "选择整个界面使用的主题和语言。",
    "settings.themeTitle": "颜色主题",
    "settings.themeDesc": "在深色和浅色仪表盘主题之间切换。",
    "settings.dark": "深色",
    "settings.light": "浅色",
    "settings.languageTitle": "界面语言",
    "settings.languageDesc": "支持英语和简体中文。",
    "settings.sessionEyebrow": "本地数据",
    "settings.sessionTitle": "会话控制",
    "settings.sessionDesc": "扫描记录保存在本地 SQLite 数据库中，保留时间由策略配置。",
    "settings.clearTitle": "清除近期扫描会话",
    "settings.clearDesc": "清除此浏览器会话中的计数器和近期扫描记录。",
    "settings.clearButton": "清除会话",
    "settings.privacyTitle": "隐私提醒",
    "settings.privacyDesc": "请避免使用真实凭据、个人记录或机密文件进行测试。",
    "settings.localBadge": "本地分析",
    "scanner.loading": "正在本地分析……",
    "scanner.emptyError": "请先输入提示内容再开始扫描。",
    "dashboard.loadError": "无法加载仪表盘数据，请刷新页面后重试。"
  };

  const categoryZh = {
    "Prompt injection": "提示注入",
    "Data exposure": "数据泄露",
    "Dangerous request": "危险请求",
    "Violent threat language": "暴力威胁语言",
    "Harmful content": "有害内容",
    "Obfuscation": "混淆与编码规避",
    "Social engineering": "社会工程",
    "Nested injection": "嵌套注入",
    "Persistent injection": "持久化注入",
    "Unauthorized tool use": "未授权工具调用",
    "Jailbreak": "越狱",
    "Indirect injection": "间接提示注入",
    "Structured injection": "结构化格式注入",
    "Output manipulation": "输出操纵",
    "Authority impersonation": "权限冒充",
    "Code injection": "代码注释注入",
    "Configured rule": "配置规则",
    "Instruction override": "指令覆盖",
    "Multilingual": "多语言",
    "Benign": "正常示例",
    "Benign security": "安全教育示例",
    "Benign multilingual": "多语言正常示例",
    "Violence or physical harm": "暴力或人身伤害",
    "Weapon or explosive construction": "武器或爆炸物制作",
    "Poisoning request": "投毒请求",
    "Self-harm or suicide intent": "自伤或自杀意图",
    "Illegal cyber activity": "非法网络活动",
    "Illegal drug production": "非法药物制造",
    "Fraud or physical break-in": "欺诈或非法闯入",
    "Chinese harmful or dangerous intent": "中文有害或危险意图",
    "Mixed Chinese-English harmful intent": "中英混合有害意图",
    "Prompt Injection": "提示注入",
    "Data Exposure": "数据泄露",
    "Local heuristic": "本地启发式检测"
  };

  const explanationZhByCategory = {
    "Prompt injection": "该规则用于识别试图覆盖原始任务或更高优先级指令的提示。",
    "Data exposure": "该规则用于识别提取或泄露隐藏提示、凭据、私人数据或内部上下文的请求。",
    "Dangerous request": "该规则用于识别可能涉及危险行为或有害请求的措辞。",
    "Violent threat language": "该规则用于识别明确的暴力威胁表达。",
    "Jailbreak": "该规则用于识别试图通过角色扮演或解除限制绕过安全策略的提示。",
    "Indirect injection": "该规则用于识别来自文档、检索结果或元数据的不可信指令。",
    "Unauthorized tool use": "该规则用于识别未经授权的工具调用或外部操作。",
    "Obfuscation": "该规则用于识别通过编码、混淆或特殊字符隐藏的指令。",
    "Social engineering": "该规则用于识别利用紧急、权威或情绪压力的绕过请求。",
    "Nested injection": "该规则用于识别嵌套或多步骤的指令覆盖。",
    "Persistent injection": "该规则用于识别试图将覆盖指令保留到后续对话的提示。",
    "Structured injection": "该规则用于识别利用 JSON、XML 或类似格式伪装特权指令的提示。",
    "Output manipulation": "该规则用于识别要求隐藏警告或以输出格式掩饰信息泄露的提示。",
    "Authority impersonation": "该规则用于识别冒充管理员或其他特权角色的请求。",
    "Code injection": "该规则用于识别嵌入代码注释或文档字符串中的指令。",
    "Policy bypass": "该规则用于识别试图以例外为由绕过安全、隐私或访问控制的提示。",
    "Credential theft": "该规则用于识别收集或披露认证凭据的请求。",
    "Data exfiltration": "该规则用于识别将敏感信息传输到未经批准位置的请求。",
    "Instruction override": "该规则用于识别试图替换原始指令的提示。",
    "Harmful content": "该规则用于识别可能涉及危险或有害意图的提示。",
    "Configured rule": "该规则用于识别与配置条件匹配的可疑提示。"
  };

  const probeZh = {
    "Instruction override": ["指令覆盖", "检查是否能检测直接的指令覆盖。"],
    "Indirect document injection": ["文档中的间接注入", "检查不可信文档中的嵌入指令。"],
    "Chinese mixed-language override": ["中英混合指令覆盖", "检查中英文混合的提示注入措辞。"],
    "Encoded instruction request": ["编码指令请求", "检查系统是否会解码并执行编码指令。"],
    "Harmful intent warning": ["有害意图警告", "检查是否会独立显示有害内容警告。"],
    "Benign summary request": ["正常摘要请求", "普通提示，不应触发有害内容警告。"],
    "Security education": ["安全教育", "检查正常的安全教育和防御语境。"],
    "Chinese benign request": ["中文正常请求", "用于检查中文教育类提示是否正常处理。"]
  };

  const ruleNameZh = {
  "Instruction override attempt": "指令覆盖尝试",
  "Hidden instruction extraction": "隐藏指令提取",
  "Jailbreak or safety bypass": "越狱或安全限制绕过",
  "Sensitive information request": "敏感信息请求",
  "Untrusted-content instruction": "不可信内容中的指令",
  "Possible data exfiltration": "疑似数据外传",
  "Dangerous weapon construction request": "危险武器制作请求",
  "Explicit violent threat language": "明确暴力威胁措辞",
  "Role or authority impersonation": "角色或权限冒充",
  "Instruction hierarchy manipulation": "指令层级操纵",
  "Forced response or instruction concealment": "强制输出或隐藏指令",
  "Tool misuse or unauthorized action": "工具滥用或未授权操作",
  "Developer instruction override": "开发者指令覆盖",
  "Fake system override": "伪造系统覆盖指令",
  "Confidential context extraction": "机密上下文提取",
  "Improvised explosive construction request": "自制爆炸物制作请求",
  "Authority impersonation for credential theft": "冒充权限以窃取凭据",
  "Harmful threat generation request": "有害威胁生成请求",
  "Direct hidden instruction request": "直接索取隐藏指令",
  "Safety restriction removal": "移除安全限制",
  "Hidden prompt extraction": "隐藏提示提取",
  "Safeguard bypass for harmful request": "为有害请求绕过防护",
  "Task replacement attempt": "任务替换尝试",
  "Internal instruction reproduction": "内部指令复现",
  "Unrestricted assistant jailbreak": "无限制助手越狱",
  "Chinese instruction override": "中文指令覆盖",
  "Chinese hidden prompt extraction": "中文隐藏提示提取",
  "Mixed Chinese-English override": "中英混合指令覆盖",
  "Encoded instruction execution": "编码指令执行",
  "Leetspeak instruction override": "Leetspeak 指令覆盖",
  "Emotional pressure to disclose secrets": "通过情绪施压索取秘密",
  "Nested multi-step override": "嵌套多步骤覆盖",
  "Persistent instruction override": "持久化指令覆盖",
  "Initial instruction or preamble extraction": "初始指令或前置提示提取",
  "Private context extraction": "私人上下文提取",
  "Tool action with sensitive prompt data": "涉及敏感提示数据的工具操作",
  "Tool sweep or unauthorized external write": "批量调用工具或未授权外部写入",
  "Chinese indirect instruction override": "中文间接指令覆盖",
  "Roleplay persona safety bypass": "角色扮演绕过安全限制",
  "Output-only secret disclosure": "仅输出秘密内容",
  "Retrieval index poisoning": "检索索引投毒",
  "Policy bypass through exception framing": "以例外为由绕过策略",
  "Credential collection or deception": "凭据收集或欺骗",
  "Discarded developer guidance": "丢弃开发者指导",
  "System prompt extraction by paraphrase": "通过改述提取系统提示",
  "Internal notes and sensitive context exfiltration": "内部备注和敏感上下文外传",
  "Sensitive data collection and external transmission": "收集敏感数据并向外传输",
  "Tool invocation to expose sensitive context": "调用工具暴露敏感上下文",
  "Urgent authority ticket override": "紧急权限工单覆盖",
  "Persona-based jailbreak and refusal suppression": "角色越狱与拒绝抑制",
  "Output format used to disguise disclosure": "利用输出格式掩饰泄露",
  "Encoded payload treated as privileged instruction": "将编码载荷当作特权指令",
  "Instruction cancellation or task replacement": "取消指令或替换任务",
  "Structured role payload with disclosure action": "带有泄露操作的结构化角色载荷",
  "Tool execution with instruction override": "带有指令覆盖的工具执行",
  "Credential collection and external destination": "收集凭据并发送到外部位置",
  "Untrusted text claims authority": "不可信文本冒充权威",
  "Encoded instruction followed": "执行编码指令",
  "Chinese privileged tool request": "中文未授权工具请求",
  "Roleplay safety bypass": "角色扮演安全绕过",
  "Indirect instruction in retrieved content": "检索内容中的间接指令",
  "Tool use without approval": "未经批准使用工具",
  "Multi-step prompt override": "多步骤提示覆盖",
  "External destination data transfer": "向外部位置传输数据",
  "Fake administrator authority": "伪造管理员权限",
  "Concealed unauthorized action": "隐藏未授权操作",
  "JSON role injection": "JSON 角色注入",
  "XML system-tag injection": "XML 系统标签注入",
  "Emotional pressure with disclosure request": "通过情绪施压要求泄露",
  "Urgency pressure with bypass request": "通过紧急压力要求绕过控制",
  "Code comment instruction injection": "代码注释指令注入",
  "Output suppression with secret disclosure": "压制说明并泄露秘密",
  "Policy exception claim": "声称适用策略例外",
  "Instruction hidden in external document": "外部文档中的隐藏指令",
  "Sensitive asset transfer to unapproved destination": "向未批准位置传输敏感资产",
  "Unauthorized tool operation or audit suppression": "未授权工具操作或审计抑制",
  "Invalid system message and task replacement": "伪称系统消息无效并替换任务",
  "Hidden system and developer message extraction": "提取隐藏的系统和开发者消息",
  "Authority claim superseding instructions": "声称权限可覆盖原有指令",
  "Indirect metadata instruction override": "通过元数据进行间接指令覆盖",
  "Policy bypass claimed as authorization": "以授权为由绕过策略"
};

  const getStored = (key, fallback) => {
    try { return localStorage.getItem(key) || fallback; } catch (_) { return fallback; }
  };
  const saveStored = (key, value) => {
    try { localStorage.setItem(key, value); } catch (_) {}
  };

  // Capture the original English labels before applying a persisted language choice.
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    if (!element.dataset.i18nEn) element.dataset.i18nEn = element.textContent;
  });
  ["placeholder", "title", "aria-label"].forEach((attribute) => {
    const selector = "[data-i18n-" + attribute.replace("aria-label", "aria-label") + "]";
    document.querySelectorAll(selector).forEach((element) => {
      const key = "i18n" + attribute.split("-").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join("");
      if (!element.dataset[key]) element.dataset[key] = element.getAttribute(attribute) || "";
    });
  });

  let language = getStored(LANGUAGE_KEY, "en");
  let theme = getStored(THEME_KEY, "dark");

  function translateCategory(value) {
    return language === "zh" ? (categoryZh[value] || value) : value;
  }
  function translateRuleName(value) {
    return language === "zh" ? (ruleNameZh[value] || value) : value;
  }

  function applyTranslations() {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.dataset.i18n;
      if (language === "zh" && Object.prototype.hasOwnProperty.call(zh, key)) {
        element.textContent = zh[key];
      } else {
        element.textContent = element.dataset.i18nEn || element.textContent;
      }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const key = element.dataset.i18nPlaceholder;
      const original = element.dataset.placeholder || element.getAttribute("placeholder") || "";
      if (!element.dataset.placeholder) element.dataset.placeholder = original;
      if (language === "zh" && zh[key]) element.setAttribute("placeholder", zh[key]);
      else element.setAttribute("placeholder", original);
    });
    document.querySelectorAll("[data-i18n-title]").forEach((element) => {
      const key = element.dataset.i18nTitle;
      const original = element.dataset.title || element.getAttribute("title") || "";
      if (!element.dataset.title) element.dataset.title = original;
      if (language === "zh" && zh[key]) element.setAttribute("title", zh[key]);
      else element.setAttribute("title", original);
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      const key = element.dataset.i18nAriaLabel;
      const original = element.dataset.ariaLabel || element.getAttribute("aria-label") || "";
      if (!element.dataset.ariaLabel) element.dataset.ariaLabel = original;
      if (language === "zh" && zh[key]) element.setAttribute("aria-label", zh[key]);
      else element.setAttribute("aria-label", original);
    });
    document.querySelectorAll("[data-risk-level]").forEach((element) => {
      const level = element.dataset.riskLevel || "";
      const map = language === "zh"
        ? { low: "低风险", medium: "中风险", high: "高风险" }
        : { low: "Low", medium: "Medium", high: "High" };
      if (element.classList.contains("risk-pill")) {
        const firstText = Array.from(element.childNodes).find((node) => node.nodeType === Node.TEXT_NODE);
        if (firstText) firstText.nodeValue = (map[level] || level) + (element.querySelector('[data-i18n="report.risk"]') ? " " : "");
      } else {
        element.textContent = map[level] || level;
      }
    });
    document.querySelectorAll("[data-category-label]").forEach((element) => {
      const category = element.dataset.categoryLabel || element.textContent;
      element.textContent = translateCategory(category);
    });
    document.querySelectorAll("[data-rule-name]").forEach((element) => {
      const name = element.dataset.ruleName;
      element.textContent = translateRuleName(name);
    });
    document.querySelectorAll("[data-rule-explanation-for]").forEach((element) => {
      const name = element.dataset.ruleExplanationFor;
      if (!element.dataset.ruleExplanationEn) element.dataset.ruleExplanationEn = element.textContent;
      if (language === "zh") {
        const category = element.dataset.ruleCategory || "Configured rule";
        element.textContent = explanationZhByCategory[category] || ("该规则用于检查与“" + translateCategory(category) + "”相关的可疑模式。");
      } else {
        element.textContent = element.dataset.ruleExplanationEn;
      }
    });
    document.querySelectorAll("[data-probe-label]").forEach((element) => {
      const label = element.dataset.probeLabel;
      element.textContent = language === "zh" ? (label === "attack" ? "攻击" : "正常") : (label === "attack" ? "Attack" : "Safe");
    });
    document.querySelectorAll("[data-probe-name]").forEach((element) => {
      const key = element.dataset.probeName;
      if (language === "zh" && probeZh[key]) element.textContent = probeZh[key][0];
      else element.textContent = key;
    });
    document.querySelectorAll("[data-probe-description]").forEach((element) => {
      const key = element.dataset.probeDescription;
      const original = element.dataset.probeDescriptionEn || element.textContent;
      if (!element.dataset.probeDescriptionEn) element.dataset.probeDescriptionEn = original;
      if (language === "zh" && probeZh[key]) element.textContent = probeZh[key][1];
      else element.textContent = original;
    });
    document.querySelectorAll("[data-summary-en]").forEach((element) => {
      element.textContent = language === "zh" ? (element.dataset.summaryZh || "已完成启发式分析，请检查匹配信号。") : element.dataset.summaryEn;
    });
    document.querySelectorAll("[data-lang]").forEach((button) => {
      const active = button.dataset.lang === language;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.querySelectorAll("[data-language-choice]").forEach((button) => button.classList.toggle("active", button.dataset.languageChoice === language));
    document.querySelectorAll("[data-theme-choice]").forEach((button) => button.classList.toggle("active", button.dataset.themeChoice === theme));
  }

  window.promptGuardTranslateCategory = translateCategory;
  window.promptGuardTranslateRuleName = translateRuleName;
  window.promptGuardGetLanguage = () => language;

  function setLanguage(next) {
    language = next === "zh" ? "zh" : "en";
    saveStored(LANGUAGE_KEY, language);
    applyTranslations();
    window.dispatchEvent(new CustomEvent("promptguard:languagechange", { detail: { language } }));
  }
  function setTheme(next) {
    theme = next === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = theme;
    saveStored(THEME_KEY, theme);
    applyTranslations();
  }
  function animateCounters() {
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.querySelectorAll("[data-counter]").forEach((element) => {
      const target = Number(element.dataset.counter || element.textContent || 0);
      if (!Number.isFinite(target)) return;
      if (reduceMotion || target === 0) {
        element.textContent = String(Math.round(target));
        return;
      }
      const start = performance.now();
      const duration = 620;
      function tick(now) {
        const progress = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - progress, 3);
        element.textContent = String(Math.round(target * eased));
        if (progress < 1) requestAnimationFrame(tick);
      }
      element.textContent = "0";
      requestAnimationFrame(tick);
    });
  }

  setTheme(theme);
  applyTranslations();
  animateCounters();
  window.dispatchEvent(new CustomEvent("promptguard:languagechange", { detail: { language } }));

  document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => setLanguage(button.dataset.lang)));
  document.querySelectorAll("[data-language-choice]").forEach((button) => button.addEventListener("click", () => setLanguage(button.dataset.languageChoice)));
  document.querySelectorAll("[data-theme-choice]").forEach((button) => button.addEventListener("click", () => setTheme(button.dataset.themeChoice)));
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) themeToggle.addEventListener("click", () => setTheme(theme === "dark" ? "light" : "dark"));

  const sidebar = document.getElementById("sidebar");
  const mobileMenu = document.getElementById("mobile-menu");
  const scrim = document.getElementById("sidebar-scrim");
  function closeSidebar() { document.body.classList.remove("sidebar-open"); }
  if (mobileMenu) mobileMenu.addEventListener("click", () => document.body.classList.toggle("sidebar-open"));
  if (scrim) scrim.addEventListener("click", closeSidebar);
  if (sidebar) sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeSidebar));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeSidebar(); });

  const textarea = document.getElementById("prompt");
  const counter = document.getElementById("char-count");
  const form = document.getElementById("scan-form");
  const scanButton = document.getElementById("scan-button");
  const clearButton = document.getElementById("clear-prompt");

  function updateCount() {
    if (!textarea || !counter) return;
    counter.textContent = textarea.value.length.toLocaleString() + " / 10,000";
    counter.classList.toggle("counter-near-limit", textarea.value.length >= 9000);
  }
  if (textarea) {
    textarea.addEventListener("input", updateCount);
    updateCount();
    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => {
        textarea.value = button.getAttribute("data-sample") || "";
        updateCount();
        textarea.focus();
      });
    });
    if (clearButton) clearButton.addEventListener("click", () => { textarea.value = ""; updateCount(); textarea.focus(); });
  }
  if (form && scanButton) {
    form.addEventListener("submit", (event) => {
      if (!textarea || !textarea.value.trim()) {
        event.preventDefault();
        if (textarea) textarea.focus();
        return;
      }
      scanButton.disabled = true;
      scanButton.setAttribute("aria-busy", "true");
      const label = scanButton.querySelector('[data-i18n="scanner.run"]');
      if (label) label.textContent = language === "zh" ? zh["scanner.loading"] : "Analyzing locally…";
    });
  }

  // Search and filter the scan-history tables without a page reload.
  const search = document.getElementById("history-search");
  const filter = document.getElementById("history-filter");
  const historyTable = document.getElementById("history-table");
  const noMatch = document.getElementById("history-no-match");
  function filterHistory() {
    if (!historyTable) return;
    const query = (search ? search.value : "").trim().toLowerCase();
    const mode = filter ? filter.value : "all";
    let visible = 0;
    historyTable.querySelectorAll("tbody tr").forEach((row) => {
      const text = row.textContent.toLowerCase();
      const matchesQuery = !query || text.includes(query);
      const matchesRisk = mode === "all" || row.dataset.risk === mode || (mode === "harmful" && row.dataset.harmful === "true");
      const show = matchesQuery && matchesRisk;
      row.hidden = !show;
      if (show) visible += 1;
    });
    if (noMatch) noMatch.hidden = visible > 0;
  }
  if (search) search.addEventListener("input", filterHistory);
  if (filter) filter.addEventListener("change", filterHistory);

  // Session clearing is an explicit local action from Settings.
  const clearSession = document.getElementById("clear-session");
  if (clearSession) clearSession.addEventListener("click", async () => {
    const feedback = document.getElementById("settings-feedback");
    clearSession.disabled = true;
    try {
      const response = await fetch("/api/clear-session", { method: "POST" });
      if (!response.ok) throw new Error("Could not clear the session.");
      if (feedback) {
        feedback.hidden = false;
        feedback.textContent = language === "zh" ? "已清除本地扫描会话。" : "Your retained scan history has been cleared.";
      }
    } catch (_) {
      if (feedback) {
        feedback.hidden = false;
        feedback.textContent = language === "zh" ? "清除失败，请刷新后重试。" : "Could not clear the session. Please refresh and try again.";
      }
    } finally {
      clearSession.disabled = false;
    }
  });
});
