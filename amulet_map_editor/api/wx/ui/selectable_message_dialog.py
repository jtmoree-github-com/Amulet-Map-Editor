"""A message dialog with selectable/copyable text."""
from typing import Optional
import wx
from amulet_map_editor.api import image


class SelectableMessageDialog(wx.Dialog):
    """
    A message dialog similar to wx.MessageBox but with selectable/copyable text.
    
    This allows users to select and copy error messages and other important text.
    """
    
    def __init__(
        self,
        parent: Optional[wx.Window],
        message: str,
        title: str = "Message",
        style: int = wx.OK | wx.ICON_INFORMATION,
        **kwargs,
    ):
        # Ensure proper dialog style
        kwargs["style"] = kwargs.get("style", 0) | wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title=title, **kwargs)
        
        self._message = message
        self._style = style
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)
        
        # Create content area with icon and text
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(content_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        # Add icon based on style
        icon_bitmap = self._get_icon_bitmap(style)
        if icon_bitmap:
            bitmap_widget = wx.StaticBitmap(self, bitmap=icon_bitmap)
            content_sizer.Add(bitmap_widget, 0, wx.RIGHT, 10)
        
        # Add selectable text using TextCtrl (allows selection/copy)
        text_ctrl = wx.TextCtrl(
            self,
            wx.ID_ANY,
            message,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_NONE,
            size=(400, -1),
        )
        # Make background match dialog background
        text_ctrl.SetBackgroundColour(self.GetBackgroundColour())
        content_sizer.Add(text_ctrl, 1, wx.EXPAND)
        
        # Create button sizer
        button_sizer = wx.StdDialogButtonSizer()
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        
        # Add Copy button only for error and warning dialogs
        if style & (wx.ICON_ERROR | wx.ICON_WARNING):
            copy_button = wx.Button(self, wx.ID_ANY, "Copy")
            copy_button.Bind(wx.EVT_BUTTON, lambda evt: self._copy_to_clipboard())
            button_sizer.Add(copy_button, 0, wx.RIGHT, 5)
        
        # Add standard buttons based on style
        if style & wx.YES_NO:
            button_yes = wx.Button(self, wx.ID_YES, "")
            button_sizer.AddButton(button_yes)
            button_no = wx.Button(self, wx.ID_NO, "")
            button_sizer.AddButton(button_no)
            if style & wx.NO_DEFAULT:
                button_no.SetDefault()
            else:
                button_yes.SetDefault()
        elif style & wx.CANCEL:
            # Has both OK and Cancel
            button_ok = wx.Button(self, wx.ID_OK, "")
            button_sizer.AddButton(button_ok)
            button_cancel = wx.Button(self, wx.ID_CANCEL, "")
            button_sizer.AddButton(button_cancel)
            button_ok.SetDefault()
        else:  # wx.OK (default)
            button_ok = wx.Button(self, wx.ID_OK, "")
            button_ok.SetDefault()
            button_sizer.AddButton(button_ok)
        
        button_sizer.Realize()
        
        self.Fit()
        self.Layout()
        
        # Ensure minimum size
        min_width = 450
        min_height = 150
        current_size = self.GetSize()
        if current_size.width < min_width or current_size.height < min_height:
            self.SetSize(max(current_size.width, min_width), max(current_size.height, min_height))
    
    def _get_icon_bitmap(self, style: int) -> Optional[wx.Bitmap]:
        """Get the appropriate icon based on the style flags."""
        if style & wx.ICON_ERROR:
            return image.icon.tablericons.alert_circle.bitmap(32, 32)
        elif style & wx.ICON_WARNING:
            return image.icon.tablericons.alert_triangle.bitmap(32, 32)
        elif style & wx.ICON_INFORMATION:
            return image.icon.tablericons.info_circle.bitmap(32, 32)
        elif style & wx.ICON_QUESTION:
            return image.icon.tablericons.help_circle.bitmap(32, 32)
        return None
    
    def _copy_to_clipboard(self):
        """Copy the message to clipboard."""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self._message))
            wx.TheClipboard.Close()


def SelectableMessageBox(
    message: str,
    title: str = "Message",
    style: int = wx.OK | wx.ICON_INFORMATION,
    parent: Optional[wx.Window] = None,
) -> int:
    """
    Show a message dialog with selectable/copyable text.
    
    This is a drop-in replacement for wx.MessageBox that allows text selection.
    
    Args:
        message: The message to display
        title: The dialog title
        style: Style flags (wx.OK, wx.YES_NO, wx.ICON_ERROR, etc.)
        parent: Parent window
    
    Returns:
        Dialog result (wx.ID_OK, wx.ID_YES, wx.ID_NO, wx.ID_CANCEL, etc.)
    """
    dialog = SelectableMessageDialog(parent, message, title, style)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result
