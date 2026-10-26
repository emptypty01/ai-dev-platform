const board = penpot.currentPage.root.children.find(shape => shape.name === '订单列表 · 桌面');
board.children.filter(shape => ['列标题', '已取消金额'].includes(shape.name)).forEach(shape => shape.remove());
function label(value, x, y, width) {
  const shape = penpot.createText(value);
  board.appendChild(shape);
  shape.x = x; shape.y = y; shape.resize(width, 30); shape.fontSize = '15';
  shape.fills = [{ fillColor: '#59687B', fillOpacity: 1 }];
}
label('商品 / 订单号', 52, 360, 300);
label('数量', 412, 360, 80);
label('总金额', 515, 360, 120);
label('状态', 650, 360, 90);
label('操作', 760, 360, 100);
label('1', 412, 530, 80);
label('¥89.00', 515, 530, 120);
label('已取消', 650, 530, 90);
label('已结束', 760, 530, 100);
return { updated: true };
