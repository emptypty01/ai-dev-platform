const page = penpot.currentPage;
if (page.root.children.some(shape => shape.name === '订单列表 · 桌面')) {
  return { skipped: true, reason: '订单原型已存在，避免重复创建' };
}
page.name = '订单管理 · 业务与验收状态';
function board(name, x, y, width, height) {
  const shape = penpot.createBoard();
  shape.name = name; shape.x = x; shape.y = y; shape.resize(width, height);
  shape.fills = [{ fillColor: '#F3F6FA', fillOpacity: 1 }];
  return shape;
}
function rect(parent, name, x, y, width, height, color) {
  const shape = penpot.createRectangle();
  parent.appendChild(shape); shape.name = name; shape.x = parent.x + x; shape.y = parent.y + y;
  shape.resize(width, height); shape.fills = [{ fillColor: color, fillOpacity: 1 }];
  return shape;
}
function text(parent, name, value, x, y, width, size = 18, color = '#263449') {
  const shape = penpot.createText(value);
  parent.appendChild(shape); shape.name = name; shape.x = parent.x + x; shape.y = parent.y + y;
  shape.fontSize = String(size); shape.fills = [{ fillColor: color, fillOpacity: 1 }];
  shape.growType = 'auto-height'; shape.resize(width, 50);
  return shape;
}
function shell(parent, subtitle) {
  rect(parent, '顶部导航', 0, 0, 1280, 76, '#FFFFFF');
  rect(parent, '品牌标记', 28, 20, 36, 36, '#184DBA');
  text(parent, '品牌文字', '订单管理', 80, 24, 300, 22);
  text(parent, '工作区', '本地演示工作区', 1040, 28, 210, 14, '#59687B');
  text(parent, '页面标题', '订单', 28, 118, 300, 34);
  text(parent, '页面说明', subtitle, 28, 168, 1100, 17, '#59687B');
}
const desktop = board('订单列表 · 桌面', 0, 0, 1280, 820);
shell(desktop, '登记商品订单，核对金额并跟进处理状态。');
rect(desktop, '订单列表区域', 28, 220, 850, 430, '#FFFFFF');
text(desktop, '列表标题', '最近订单', 52, 244, 400, 22);
text(desktop, '状态筛选', '全部       待处理       已取消', 52, 298, 700, 18, '#184DBA');
rect(desktop, '表头背景', 28, 345, 850, 48, '#F8FAFC');
text(desktop, '列标题', '商品 / 订单号                         数量           总金额           状态          操作', 52, 360, 810, 15, '#59687B');
text(desktop, '示例商品', '机械键盘', 52, 424, 250, 20);
text(desktop, '示例订单号', 'OD-6c20…a718', 52, 456, 300, 14, '#64748B');
text(desktop, '示例数量', '3', 412, 434, 70, 18);
text(desktop, '示例金额', '¥59.70', 515, 434, 120, 18);
rect(desktop, '待处理标签', 650, 426, 80, 34, '#FFF3D5');
text(desktop, '待处理文字', '待处理', 662, 432, 80, 15, '#835400');
text(desktop, '取消操作', '取消订单', 760, 434, 110, 15, '#B53731');
text(desktop, '已取消商品', '办公鼠标', 52, 520, 250, 20);
text(desktop, '已取消金额', '1                 ¥89.00            已取消          已结束', 412, 530, 450, 16, '#59687B');
text(desktop, '列表限制', '显示最近 100 笔订单 · 金额以人民币计', 52, 613, 700, 13, '#64748B');
rect(desktop, '创建订单区域', 902, 220, 350, 430, '#FFFFFF');
rect(desktop, '创建区域顶边', 902, 220, 350, 3, '#184DBA');
text(desktop, '创建标题', '创建订单', 926, 245, 300, 22);
text(desktop, '金额提示', '总金额按数量与单价自动计算。', 926, 286, 300, 15, '#59687B');
text(desktop, '商品字段标签', '商品名称', 926, 340, 260, 17);
rect(desktop, '商品输入框', 926, 375, 300, 44, '#F3F6FA');
text(desktop, '商品输入示意', '例如：机械键盘', 938, 385, 280, 16, '#64748B');
text(desktop, '数量价格标签', '数量                 单价（元）', 926, 448, 300, 17);
rect(desktop, '数量输入框', 926, 482, 85, 44, '#F3F6FA');
rect(desktop, '单价输入框', 1027, 482, 199, 44, '#F3F6FA');
text(desktop, '数量默认值', '1', 940, 491, 70, 17);
text(desktop, '单价占位', '0.00', 1042, 491, 160, 17, '#64748B');
rect(desktop, '创建按钮', 926, 560, 300, 46, '#184DBA');
text(desktop, '创建按钮文字', '创建订单', 1030, 571, 170, 18, '#FFFFFF');
text(desktop, '验收注记', 'AC-01 创建与精确金额  ·  AC-02 列表与筛选  ·  AC-04 取消需确认，重复取消保持结果', 28, 718, 1220, 17, '#184DBA');
const states = board('空状态 · 校验 · 取消规则', 1400, 0, 1280, 820);
shell(states, '研发交接基线：成功、空数据、失败及重复操作必须有明确行为。');
rect(states, '空状态容器', 28, 220, 1224, 160, '#FFFFFF');
text(states, '空状态标题', '暂无订单', 70, 253, 1100, 25);
text(states, '空状态引导', '填写商品名称、数量和单价，创建第一笔订单。', 70, 305, 1100, 19, '#59687B');
rect(states, '校验错误容器', 28, 410, 1224, 120, '#FFF0EF');
text(states, '校验错误提示', '请检查商品名称、数量和单价的填写范围。', 70, 440, 1120, 22, '#9B2C25');
text(states, '校验边界', 'AC-03：名称 1–80 字；数量 1–1000；单价 0.01–99999999.99，最多两位小数。', 70, 483, 1120, 16, '#9B2C25');
rect(states, '状态规则容器', 28, 560, 1224, 180, '#FFFFFF');
text(states, '状态规则标题', '取消订单', 70, 586, 1120, 24);
text(states, '状态规则说明', 'NEW → CANCELLED；操作前确认；重复取消返回同一结果；不存在的订单返回 404。\nAC-05：刷新与服务重启后保留记录。支付、库存与权限不在本次示例范围。', 70, 633, 1120, 18);
penpot.selection = [desktop, states];
return { pageId: page.id, boards: [{ id: desktop.id, name: desktop.name }, { id: states.id, name: states.name }], shapes: page.root.children.length };
