const resume = require("../../data/resume");

Page({
  data: {
    ...resume,
    heroImage: "/assets/resume-hero.webp"
  },

  callPhone() {
    wx.makePhoneCall({
      phoneNumber: this.data.profile.phone
    });
  },

  copyEmail() {
    wx.setClipboardData({
      data: this.data.profile.email,
      success: () => {
        wx.showToast({
          title: "\u90ae\u7bb1\u5df2\u590d\u5236",
          icon: "success"
        });
      }
    });
  },

  showSkill(event) {
    const { name, desc } = event.currentTarget.dataset;

    wx.showModal({
      title: name,
      content: desc,
      showCancel: false,
      confirmText: "\u77e5\u9053\u4e86"
    });
  },

  goExperience() {
    wx.switchTab({
      url: "/pages/experience/experience"
    });
  },

  onShareAppMessage() {
    return {
      title: "\u8d44\u6d77\u6625 | \u6444\u5f71\u5e08 / \u526a\u8f91\u540e\u671f / \u65b0\u5a92\u4f53\u8fd0\u8425",
      path: "/pages/index/index",
      imageUrl: this.data.heroImage
    };
  }
});
