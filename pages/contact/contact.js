const resume = require("../../data/resume");

Page({
  data: {
    profile: resume.profile,
    targets: resume.targets,
    ui: resume.ui
  },

  callPhone() {
    wx.makePhoneCall({
      phoneNumber: this.data.profile.phone
    });
  },

  copyPhone() {
    wx.setClipboardData({
      data: this.data.profile.phone,
      success: () => wx.showToast({ title: "\u7535\u8bdd\u5df2\u590d\u5236", icon: "success" })
    });
  },

  copyEmail() {
    wx.setClipboardData({
      data: this.data.profile.email,
      success: () => wx.showToast({ title: "\u90ae\u7bb1\u5730\u5740\u5df2\u590d\u5236", icon: "success" })
    });
  },

  copyLocation() {
    wx.setClipboardData({
      data: this.data.profile.location,
      success: () => wx.showToast({ title: "\u6240\u5728\u5730\u5df2\u590d\u5236", icon: "success" })
    });
  },

  onShareAppMessage() {
    return {
      title: "\u8054\u7cfb\u8d44\u6d77\u6625",
      path: "/pages/contact/contact"
    };
  }
});
