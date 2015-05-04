# Load some image rescources (icons etc.)
class ImRes:
    def __init__(self):
        self.summer_im = wx.Image("icons/summer-icon.png")
        self.summer_im.SetMaskFromImage(self.summer_im,231,255,255)
        self.summer = self.summer_im.ConvertToBitmap()

        self.winter_im = wx.Image("icons/winter-icon.png")
        self.winter_im.SetMaskFromImage(self.winter_im,231,255,255)
        self.winter = self.winter_im.ConvertToBitmap()

        self.front_im = wx.Image("icons/frontimage-icon.png")
        self.front_im.SetMaskFromImage(self.front_im,231,255,255)
        self.front = self.front_im.ConvertToBitmap()

        self.back_im = wx.Image("icons/backimage-icon.png")
        self.back_im.SetMaskFromImage(self.back_im,231,255,255)
        self.back = self.back_im.ConvertToBitmap()

        self.north_im = wx.Image("icons/north-icon.png")
        self.north_im.SetMaskFromImage(self.north_im,231,255,255)
        self.north = self.north_im.ConvertToBitmap()

        self.east_im = wx.Image("icons/east-icon.png")
        self.east_im.SetMaskFromImage(self.east_im,231,255,255)
        self.east = self.east_im.ConvertToBitmap()

        self.south_im = wx.Image("icons/south-icon.png")
        self.south_im.SetMaskFromImage(self.south_im,231,255,255)
        self.south = self.south_im.ConvertToBitmap()

        self.west_im = wx.Image("icons/west-icon.png")
        self.west_im.SetMaskFromImage(self.west_im,231,255,255)
        self.west = self.west_im.ConvertToBitmap()

        self.reload_im = wx.Image("icons/reloadfile-icon.png")
        self.reload_im.SetMaskFromImage(self.reload_im,231,255,255)
        self.reload = self.reload_im.ConvertToBitmap()

        self.sameforall_im = wx.Image("icons/sameforall-icon.png")
        self.sameforall_im.SetMaskFromImage(self.sameforall_im,231,255,255)
        self.sameforall = self.sameforall_im.ConvertToBitmap()

        self.center_im = wx.Image("icons/center-icon.png")
        self.center_im.SetMaskFromImage(self.center_im,231,255,255)
        self.center = self.center_im.ConvertToBitmap()

        self.x = wx.Image("icons/up-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.up = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/up2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.up2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.down = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.down2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/left-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.left = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/left2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.left2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/right-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.right = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/right2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.right2 = self.x.ConvertToBitmap()
