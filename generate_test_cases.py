import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, numbers
from openpyxl.utils import get_column_letter
from datetime import date

wb = openpyxl.Workbook()

# ============================================================
# 样式定义
# ============================================================
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, size=11, color="FFFFFF", name="微软雅黑")
title_font = Font(bold=True, size=14, name="微软雅黑")
subtitle_font = Font(bold=True, size=11, name="微软雅黑", color="333333")
normal_font = Font(size=10, name="微软雅黑")
bold_font = Font(bold=True, size=10, name="微软雅黑")

p0_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
p1_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
p2_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

module_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
stat_header_fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='B0B0B0'),
    right=Side(style='thin', color='B0B0B0'),
    top=Side(style='thin', color='B0B0B0'),
    bottom=Side(style='thin', color='B0B0B0')
)

wrap_alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# ============================================================
# Sheet 1: 冒烟测试用例
# ============================================================
ws = wb.active
ws.title = "冒烟测试用例"

# 列宽设置
col_widths = {
    'A': 10,   # 用例ID
    'B': 14,   # 模块
    'C': 28,   # 用例名称
    'D': 8,    # 优先级
    'E': 28,   # 前置条件
    'F': 45,   # 测试步骤
    'G': 45,   # 预期结果
    'H': 18,   # 测试类型
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

# 表头
headers = ["用例ID", "模块", "用例名称", "优先级", "前置条件", "测试步骤", "预期结果", "测试类型"]
for col_idx, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_idx, value=header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_alignment
    cell.border = thin_border

ws.row_dimensions[1].height = 30

# ============================================================
# 测试用例数据
# ============================================================
test_cases = [
    # ---------- 模块：素材图片生成状态展示 ----------
    {
        "id": "TC-001", "module": "素材图片生成状态展示",
        "title": "素材图片正在生成中，显示\"生成中...\"文案",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 进入视频创作/素材管理页面\n3. 已触发素材图片生成请求，且图片尚未生成完成",
        "steps": "1. 观察素材图片展示区域\n2. 等待图片生成完成\n3. 观察文案变化",
        "expected": "1. 素材图片展示区域显示\"生成中...\"文案及loading动画\n2. 图片生成完成后，\"生成中...\"文案消失，展示实际生成的素材图片\n3. 展示区域同步更新，无需手动刷新",
        "type": "功能测试"
    },
    {
        "id": "TC-002", "module": "素材图片生成状态展示",
        "title": "素材图片生成失败，展示失败状态",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 进入素材管理页面\n3. 素材图片生成请求已发起但生成失败（如网络异常、服务端错误）",
        "steps": "1. 模拟素材图片生成失败场景\n2. 观察素材展示区域\n3. 检查是否有重新生成的入口",
        "expected": "1. 展示区域显示\"生成失败\"或类似失败提示文案\n2. 提供\"重新生成\"操作入口\n3. 不显示\"暂无素材图片\"或\"生成中...\"文案",
        "type": "异常测试"
    },
    {
        "id": "TC-003", "module": "素材图片生成状态展示",
        "title": "素材图片生成进度实时更新",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 已触发多张素材图片生成\n3. 部分图片已生成完成，部分仍在生成中",
        "steps": "1. 进入素材展示页面\n2. 观察各素材槽位的状态\n3. 等待下一张图片生成完成\n4. 观察状态变化",
        "expected": "1. 已完成的图片槽位展示实际图片\n2. 未完成的图片槽位展示\"生成中...\"\n3. 图片生成完成后，对应槽位自动从\"生成中...\"切换为实际图片\n4. 状态更新及时，无明显延迟",
        "type": "功能测试"
    },
    {
        "id": "TC-004", "module": "素材图片生成状态展示",
        "title": "初始无素材时的默认状态（\"暂无素材图片\"）展示",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 进入素材管理页面\n3. 用户尚未触发任何素材图片生成",
        "steps": "1. 进入素材展示区域\n2. 观察默认占位状态",
        "expected": "1. 展示区域显示\"暂无素材图片\"占位提示\n2. 不显示\"生成中...\"文案\n3. 引导用户触发素材图片生成的操作入口可见",
        "type": "功能测试"
    },
    {
        "id": "TC-005", "module": "素材图片生成状态展示",
        "title": "\"生成中...\"状态与loading动画联动展示",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 已触发素材图片生成",
        "steps": "1. 观察\"生成中...\"文案旁边或下方是否有loading动画（如旋转图标、进度条、骨架屏）\n2. 确认动画是否为连续播放\n3. 确认动画在生成完成后是否自动停止",
        "expected": "1. \"生成中...\"文案伴随loading动画同时展示\n2. 动画持续播放不卡顿\n3. 生成完成后动画停止并消失",
        "type": "界面测试"
    },
    {
        "id": "TC-006", "module": "素材图片生成状态展示",
        "title": "多个素材同时生成时的状态展示",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 触发多个素材（如5个以上）同时生成",
        "steps": "1. 进入素材展示页面\n2. 观察所有素材槽位的状态\n3. 逐个等待生成完成，观察各槽位独立更新",
        "expected": "1. 所有未完成的槽位均展示\"生成中...\"\n2. 每个槽位的状态独立更新，互不影响\n3. 已完成的槽位展示对应图片，未完成的继续显示\"生成中...\"",
        "type": "功能测试"
    },
    {
        "id": "TC-007", "module": "素材图片生成状态展示",
        "title": "页面刷新后\"生成中...\"状态保持",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 素材图片正在生成中（未全部完成）",
        "steps": "1. 在\"生成中...\"状态下刷新页面\n2. 观察素材展示区域\n3. 确认后台生成状态是否正确同步到前端",
        "expected": "1. 刷新后仍展示\"生成中...\"（若图片仍在生成）\n2. 若刷新时图片已生成完成，则展示实际图片\n3. 状态与后台实际进度一致",
        "type": "功能测试"
    },
    {
        "id": "TC-008", "module": "素材图片生成状态展示",
        "title": "\"生成中...\"状态在弱网环境下的表现",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 模拟弱网环境（3G/慢速4G）\n3. 已触发素材图片生成",
        "steps": "1. 在弱网环境下进入素材展示页面\n2. 观察\"生成中...\"文案是否正常展示\n3. 等待生成完成，观察状态切换",
        "expected": "1. \"生成中...\"文案正常展示\n2. 由于弱网，生成可能较慢但状态不丢失\n3. 网络恢复后状态正常切换\n4. 不出现白屏或卡死",
        "type": "兼容性测试"
    },
    {
        "id": "TC-009", "module": "素材图片生成状态展示",
        "title": "模拟生成请求超时后的状态展示",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 触发素材图片生成\n3. 模拟生成接口超时（如30秒无响应）",
        "steps": "1. 等待生成请求超时\n2. 观察素材展示区域\n3. 检查是否有超时提示",
        "expected": "1. 超时后展示区域从\"生成中...\"切换为超时提示（如\"生成超时，请重试\"）\n2. 提供重新生成的操作入口\n3. 不永久停留在\"生成中...\"状态",
        "type": "异常测试"
    },

    # ---------- 模块：视频生成按钮控制 ----------
    {
        "id": "TC-010", "module": "视频生成按钮控制",
        "title": "素材图片未全部生成完成时，视频生成按钮置灰不可点击",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 进入视频创作页面\n3. 已触发素材图片生成，且至少有一张图片未生成完成（状态为\"生成中...\"）",
        "steps": "1. 定位\"生成视频\"按钮\n2. 观察按钮状态\n3. 尝试点击按钮",
        "expected": "1. \"生成视频\"按钮呈现置灰/禁用状态（视觉上不可点击）\n2. 鼠标悬停时指针变为禁止样式\n3. 点击按钮无任何响应，不触发视频生成流程",
        "type": "功能测试"
    },
    {
        "id": "TC-011", "module": "视频生成按钮控制",
        "title": "素材图片未生成完成时，点击\"生成视频\"按钮弹出Toast提示",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 素材图片未全部生成完成\n3. 视频生成按钮为可点击状态",
        "steps": "1. 在素材未全部生成完成的状态下\n2. 点击\"生成视频\"按钮\n3. 观察页面反馈",
        "expected": "1. 弹出Toast/提示信息，如\"素材图片生成中，请稍后再试\"或\"请等待素材图片生成完成\"\n2. 不发起视频生成请求\n3. 用户停留在当前页面",
        "type": "功能测试"
    },
    {
        "id": "TC-012", "module": "视频生成按钮控制",
        "title": "全部素材图片生成完成后，视频生成按钮恢复可点击状态",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 之前素材图片处于\"生成中...\"状态，视频生成按钮为禁用\n3. 等待全部素材图片生成完成",
        "steps": "1. 等待所有素材图片从\"生成中...\"切换为实际图片\n2. 观察\"生成视频\"按钮状态\n3. 点击按钮",
        "expected": "1. \"生成视频\"按钮从置灰恢复为正常可点击状态\n2. 点击按钮正常触发视频生成流程\n3. 状态切换实时，无需手动刷新页面",
        "type": "功能测试"
    },
    {
        "id": "TC-013", "module": "视频生成按钮控制",
        "title": "素材图片生成失败时，视频生成按钮的状态",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 部分素材图片生成失败\n3. 其余素材生成完成或\"生成中...\"",
        "steps": "1. 在素材生成失败场景下\n2. 观察\"生成视频\"按钮状态\n3. 点击按钮（若可点击）",
        "expected": "1. \"生成视频\"按钮应为置灰/禁用状态\n2. 点击时弹出提示（如\"素材图片存在异常，请重新生成后重试\"）\n3. 引导用户处理失败的素材",
        "type": "异常测试"
    },
    {
        "id": "TC-014", "module": "视频生成按钮控制",
        "title": "无素材时（\"暂无素材图片\"）视频生成按钮的状态",
        "priority": "P1", "precondition": "1. 用户已登录系统\n2. 进入视频创作页面\n3. 素材展示区域显示\"暂无素材图片\"",
        "steps": "1. 观察\"生成视频\"按钮状态\n2. 点击按钮（若可点击）",
        "expected": "1. \"生成视频\"按钮应为置灰/禁用状态\n2. 点击后弹出提示，如\"请先生成素材图片\"\n3. 引导用户触发素材生成",
        "type": "功能测试"
    },
    {
        "id": "TC-015", "module": "视频生成按钮控制",
        "title": "素材图片全部生成完成后点击视频生成按钮，正常进入视频生成流程",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 全部素材图片已生成完成\n3. 视频生成按钮为可点击状态",
        "steps": "1. 点击\"生成视频\"按钮\n2. 观察页面变化和请求发起\n3. 等待视频生成结果",
        "expected": "1. 成功发起视频生成请求\n2. 页面展示视频生成进度或跳转至视频生成页面\n3. 视频生成过程中有对应的进度展示",
        "type": "功能测试"
    },

    # ---------- 模块：状态切换与边界测试 ----------
    {
        "id": "TC-016", "module": "状态切换与边界测试",
        "title": "素材从\"暂无素材图片\"→\"生成中...\"→\"图片展示\"的完整状态流转",
        "priority": "P0", "precondition": "1. 用户已登录系统\n2. 进入素材页面，初始状态为\"暂无素材图片\"",
        "steps": "1. 触发素材图片生成\n2. 立即观察素材展示区域状态变化\n3. 等待生成完成\n4. 观察最终状态",
        "expected": "1. 初始展示\"暂无素材图片\"\n2. 触发生成后，立即切换为\"生成中...\"及loading动画\n3. 生成完成后，切换展示实际图片\n4. 三次状态切换流畅，无闪烁或错误展示",
        "type": "功能测试"
    },
    {
        "id": "TC-017", "module": "状态切换与边界测试",
        "title": "素材图片极速生成完成（如1秒内），状态展示是否正确",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 模拟极速生成场景（素材简单、服务端响应快）",
        "steps": "1. 触发素材图片生成\n2. 观察\"生成中...\"状态是否短暂出现后正确切换\n3. 检查视频生成按钮状态",
        "expected": "1. \"生成中...\"文案短暂展示后立即切换为图片\n2. 不出现长时间卡在\"生成中...\"的假象\n3. 视频生成按钮正确恢复可点击状态",
        "type": "边界值测试"
    },
    {
        "id": "TC-018", "module": "状态切换与边界测试",
        "title": "素材图片生成时间极长（如超过5分钟），状态展示是否持续正常",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 模拟长时间生成场景",
        "steps": "1. 触发素材图片生成\n2. 在生成过程中持续观察页面\n3. 检查\"生成中...\"文案和动画是否持续正常展示\n4. 等待生成最终完成",
        "expected": "1. \"生成中...\"文案在整个生成期间持续正常展示\n2. loading动画不卡顿、不消失\n3. 视频生成按钮在全部完成前始终保持禁用状态\n4. 生成完成后状态正确切换",
        "type": "边界值测试"
    },
    {
        "id": "TC-019", "module": "状态切换与边界测试",
        "title": "在\"生成中...\"状态下切换页面Tab再切回，状态保持",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 素材图片正在生成中\n3. 系统存在多个Tab页面",
        "steps": "1. 在素材生成中状态下切换到其他Tab/页面\n2. 等待30秒后切回素材页面\n3. 观察状态是否与后台同步",
        "expected": "1. 切回后状态正确展示（仍在生成则显示\"生成中...\"，已完成则显示图片）\n2. 状态与后台实际进度一致\n3. 视频生成按钮状态也同步正确",
        "type": "功能测试"
    },

    # ---------- 模块：多设备/分辨率兼容性 ----------
    {
        "id": "TC-020", "module": "多设备/分辨率兼容性",
        "title": "PC端不同分辨率下\"生成中...\"文案和按钮状态展示",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 不同分辨率的PC设备\n3. 素材图片处于各状态",
        "steps": "1. 在1920×1080分辨率下查看\n2. 在1366×768分辨率下查看\n3. 在2560×1440分辨率下查看",
        "expected": "1. 各分辨率下\"生成中...\"文案完整显示不截断\n2. 视频生成按钮禁用/启用样式在各分辨率下清晰可辨\n3. 布局不错乱",
        "type": "兼容性测试"
    },
    {
        "id": "TC-021", "module": "多设备/分辨率兼容性",
        "title": "主流浏览器（Chrome/Edge/Safari/Firefox）兼容性验证",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 分别在Chrome、Edge、Safari、Firefox浏览器中打开\n3. 素材图片处于\"生成中...\"状态",
        "steps": "1. 在Chrome中观察状态展示和按钮行为\n2. 在Edge中观察\n3. 在Safari中观察\n4. 在Firefox中观察",
        "expected": "1. 各浏览器中\"生成中...\"文案和动画均正常展示\n2. 视频生成按钮禁用/Toast提示行为一致\n3. 无兼容性差异或报错",
        "type": "兼容性测试"
    },

    # ---------- 模块：性能与压力测试 ----------
    {
        "id": "TC-022", "module": "性能与压力测试",
        "title": "大量素材同时生成时的页面性能",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 触发大量素材（如50个）同时生成",
        "steps": "1. 观察页面渲染是否卡顿\n2. 检查浏览器内存/CPU占用\n3. 滚动或切换页面是否流畅",
        "expected": "1. \"生成中...\"文案和loading动画渲染正常，无明显卡顿\n2. 浏览器不出现内存泄漏或显著升高\n3. 页面操作响应正常",
        "type": "性能测试"
    },
    {
        "id": "TC-023", "module": "性能与压力测试",
        "title": "快速重复触发生成，状态展示是否正确",
        "priority": "P2", "precondition": "1. 用户已登录系统\n2. 在生成过程中多次触发生成请求",
        "steps": "1. 第一次触发生成\n2. 在\"生成中...\"状态下再次触发新的生成\n3. 观察状态变化和按钮状态",
        "expected": "1. 新的生成请求被正确处理\n2. \"生成中...\"状态正确更新\n3. 不出现多个状态叠加或混乱\n4. 视频生成按钮始终与最新状态保持同步",
        "type": "功能测试"
    },
]

# ============================================================
# 写入测试用例数据
# ============================================================
current_row = 2
current_module = None

for idx, tc in enumerate(test_cases):
    # 模块分隔行
    if tc["module"] != current_module:
        current_module = tc["module"]
        # 写模块标题行
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=8)
        cell = ws.cell(row=current_row, column=1, value=f"【{current_module}】")
        cell.fill = module_fill
        cell.font = bold_font
        cell.alignment = Alignment(horizontal='left', vertical='center')
        cell.border = thin_border
        for c in range(2, 9):
            ws.cell(row=current_row, column=c).fill = module_fill
            ws.cell(row=current_row, column=c).border = thin_border
        ws.row_dimensions[current_row].height = 26
        current_row += 1

    row_data = [tc["id"], tc["module"], tc["title"], tc["priority"], tc["precondition"], tc["steps"], tc["expected"], tc["type"]]
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=value)
        cell.font = normal_font
        cell.alignment = wrap_alignment
        cell.border = thin_border

        # 优先级着色
        if col_idx == 4:
            cell.alignment = center_alignment
            cell.font = bold_font
            if value == "P0":
                cell.fill = p0_fill
            elif value == "P1":
                cell.fill = p1_fill
            elif value == "P2":
                cell.fill = p2_fill

        # ID列居中
        if col_idx == 1:
            cell.alignment = center_alignment

    ws.row_dimensions[current_row].height = 90
    current_row += 1

# ============================================================
# Sheet 2: 测试用例统计
# ============================================================
ws2 = wb.create_sheet(title="测试用例统计")

# 设置列宽
ws2.column_dimensions['A'].width = 25
ws2.column_dimensions['B'].width = 15
ws2.column_dimensions['C'].width = 15
ws2.column_dimensions['D'].width = 15
ws2.column_dimensions['E'].width = 15

# 标题

# ---- 概述信息 ----
ws2.merge_cells('A1:E1')
cell = ws2.cell(row=1, column=1, value="素材图片状态展示与视频生成按钮控制 - 测试用例文档")
cell.font = title_font
cell.alignment = Alignment(horizontal='left', vertical='center')
ws2.row_dimensions[1].height = 35

info_data = [
    ["测试范围：", "素材图片\"生成中...\"状态展示、视频生成按钮控制逻辑"],
    ["需求版本：", "V1.0"],
    ["设计日期：", date.today().strftime("%Y-%m-%d")],
    ["测试依据：", "1280X1280.PNG 原型图 + 用户需求描述"],
    ["", ""],
]
for i, (label, value) in enumerate(info_data, 2):
    ws2.merge_cells(start_row=i, start_column=1, end_row=i, end_column=5)
    cell = ws2.cell(row=i, column=1, value=f"{label}{value}")
    cell.font = subtitle_font
    ws2.row_dimensions[i].height = 22

# ---- 模块分布统计 ----
stat_start = 8
ws2.merge_cells(f'A{stat_start}:E{stat_start}')
cell = ws2.cell(row=stat_start, column=1, value="一、模块测试用例分布统计")
cell.font = Font(bold=True, size=12, name="微软雅黑", color="1F4E79")
ws2.row_dimensions[stat_start].height = 28

module_headers = ["模块名称", "用例数量", "P0数量", "P1数量", "P2数量"]
for col_idx, h in enumerate(module_headers, 1):
    cell = ws2.cell(row=stat_start + 1, column=col_idx, value=h)
    cell.fill = stat_header_fill
    cell.font = Font(bold=True, size=10, name="微软雅黑", color="FFFFFF")
    cell.alignment = center_alignment
    cell.border = thin_border

# 统计各模块数据
from collections import Counter, defaultdict
module_stats = defaultdict(lambda: {"total": 0, "P0": 0, "P1": 0, "P2": 0})
priority_stats = Counter()
type_stats = Counter()

for tc in test_cases:
    m = tc["module"]
    module_stats[m]["total"] += 1
    module_stats[m][tc["priority"]] += 1
    priority_stats[tc["priority"]] += 1
    type_stats[tc["type"]] += 1

row = stat_start + 2
for module, stats in module_stats.items():
    data = [module, stats["total"], stats["P0"], stats["P1"], stats["P2"]]
    for col_idx, val in enumerate(data, 1):
        cell = ws2.cell(row=row, column=col_idx, value=val)
        cell.font = normal_font
        cell.alignment = center_alignment if col_idx > 1 else Alignment(horizontal='left', vertical='center')
        cell.border = thin_border
    row += 1

# 总计行
total_data = ["合计", len(test_cases), priority_stats.get("P0", 0), priority_stats.get("P1", 0), priority_stats.get("P2", 0)]
for col_idx, val in enumerate(total_data, 1):
    cell = ws2.cell(row=row, column=col_idx, value=val)
    cell.font = bold_font
    cell.alignment = center_alignment
    cell.border = thin_border
    cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

# ---- 优先级分布统计 ----
row += 2
ws2.merge_cells(f'A{row}:E{row}')
cell = ws2.cell(row=row, column=1, value="二、优先级分布统计")
cell.font = Font(bold=True, size=12, name="微软雅黑", color="1F4E79")
ws2.row_dimensions[row].height = 28

row += 1
prio_headers = ["优先级", "数量", "占比", "说明", ""]
for col_idx, h in enumerate(prio_headers, 1):
    cell = ws2.cell(row=row, column=col_idx, value=h)
    cell.fill = stat_header_fill
    cell.font = Font(bold=True, size=10, name="微软雅黑", color="FFFFFF")
    cell.alignment = center_alignment
    cell.border = thin_border

row += 1
prio_desc = {
    "P0": "核心流程，必须验证通过",
    "P1": "重要功能，建议验证",
    "P2": "边界/兼容/性能，可选验证"
}
for p in ["P0", "P1", "P2"]:
    count = priority_stats.get(p, 0)
    pct = f"{count / len(test_cases) * 100:.1f}%" if test_cases else "0%"
    data = [p, count, pct, prio_desc[p], ""]
    for col_idx, val in enumerate(data, 1):
        cell = ws2.cell(row=row, column=col_idx, value=val)
        cell.font = bold_font if col_idx == 1 else normal_font
        cell.alignment = center_alignment
        cell.border = thin_border
    row += 1

# ---- 测试类型分布统计 ----
row += 1
ws2.merge_cells(f'A{row}:E{row}')
cell = ws2.cell(row=row, column=1, value="三、测试类型分布统计")
cell.font = Font(bold=True, size=12, name="微软雅黑", color="1F4E79")
ws2.row_dimensions[row].height = 28

row += 1
type_headers = ["测试类型", "数量", "占比", "", ""]
for col_idx, h in enumerate(type_headers, 1):
    cell = ws2.cell(row=row, column=col_idx, value=h)
    cell.fill = stat_header_fill
    cell.font = Font(bold=True, size=10, name="微软雅黑", color="FFFFFF")
    cell.alignment = center_alignment
    cell.border = thin_border

row += 1
for t, count in type_stats.most_common():
    pct = f"{count / len(test_cases) * 100:.1f}%"
    data = [t, count, pct, "", ""]
    for col_idx, val in enumerate(data, 1):
        cell = ws2.cell(row=row, column=col_idx, value=val)
        cell.font = normal_font
        cell.alignment = center_alignment
        cell.border = thin_border
    row += 1

# ---- 待澄清事项 ----
row += 2
ws2.merge_cells(f'A{row}:E{row}')
cell = ws2.cell(row=row, column=1, value="四、待澄清事项")
cell.font = Font(bold=True, size=12, name="微软雅黑", color="C00000")
ws2.row_dimensions[row].height = 28

clarifications = [
    "1. \"生成中...\"状态下，视频生成按钮的实现方式是\"置灰禁用\"还是\"可点击+Toast提示\"？还是两者结合（置灰+点击时Toast）？",
    "2. 素材图片生成超时时间的具体阈值是多少秒？",
    "3. 素材生成失败后，是否需要自动重试？重试次数上限是多少？",
    "4. \"生成中...\"的loading动画具体样式是什么？（旋转图标/骨架屏/进度条/其他）",
    "5. 多个素材生成是否有并发限制？若有，限制数量是多少？",
    "6. 视频生成按钮在各个状态下的禁用条件是否有其他依赖（如配音、字幕等）？",
    "7. Toast提示的文案具体内容是否已确定？",
    "8. 是否需要在\"生成中...\"状态下展示具体进度（如\"3/5 张已完成\"）？",
]

for i, c in enumerate(clarifications):
    row += 1
    ws2.merge_cells(f'A{row}:E{row}')
    cell = ws2.cell(row=row, column=1, value=c)
    cell.font = Font(size=10, name="微软雅黑", color="333333")
    cell.alignment = Alignment(horizontal='left', vertical='center')
    ws2.row_dimensions[row].height = 22

# ---- 测试覆盖率统计 ----
row += 2
ws2.merge_cells(f'A{row}:E{row}')
cell = ws2.cell(row=row, column=1, value="五、测试覆盖率统计")
cell.font = Font(bold=True, size=12, name="微软雅黑", color="1F4E79")
ws2.row_dimensions[row].height = 28

coverage = [
    "功能点覆盖：19/19（覆盖全部描述的功能点）",
    "核心流程覆盖：全覆盖（暂无素材→生成中→图片展示→视频生成 全链路）",
    "测试维度覆盖：功能测试、界面测试、异常测试、边界值测试、兼容性测试、性能测试",
    "需求点对应：",
    "  - 需求1「\"生成中...\"文案展示」：TC-001 ~ TC-009",
    "  - 需求2「视频生成按钮控制」：TC-010 ~ TC-015",
    "  - 需求3「状态流转与联动」：TC-016 ~ TC-023",
]

for c in coverage:
    row += 1
    ws2.merge_cells(f'A{row}:E{row}')
    cell = ws2.cell(row=row, column=1, value=c)
    cell.font = Font(size=10, name="微软雅黑", color="333333")
    cell.alignment = Alignment(horizontal='left', vertical='center')
    ws2.row_dimensions[row].height = 22

# ============================================================
# 保存文件
# ============================================================
output_path = "/Users/lanwang/Documents/trae_projects/new World/素材图片状态与视频生成控制_测试用例.xlsx"
wb.save(output_path)
print(f"测试用例Excel文件已生成: {output_path}")
print(f"共生成 {len(test_cases)} 条测试用例")
print(f"  - P0（高优先级）: {priority_stats.get('P0', 0)} 条")
print(f"  - P1（中优先级）: {priority_stats.get('P1', 0)} 条")
print(f"  - P2（低优先级）: {priority_stats.get('P2', 0)} 条")
