from PySide6.QtCore import QRect, QSize, QRectF
from PySide6.QtGui import QBrush, QPixmap, QColor, QTextDocument, QAbstractTextDocumentLayout
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

class HTMLDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()
        self.doc = QTextDocument()

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        if options.state & QStyle.State_Selected:
            background_color = QColor("#BBDEFB")
            painter.fillRect(options.rect, background_color)
        painter.save()
        self.doc.setTextWidth(options.rect.width())
        self.doc.setHtml(options.text)
        self.doc.setDefaultFont(options.font)
        options.text = ''
        # options.widget.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, options, painter)
        painter.translate(options.rect.left(), options.rect.top())
        clip = QRectF(0, 0, options.rect.width(), options.rect.height())
        painter.setClipRect(clip)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.clip = clip
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        self.doc.setHtml(option.text)
        self.doc.setTextWidth(option.rect.width())
        return QSize(self.doc.idealWidth(), self.doc.size().height())
