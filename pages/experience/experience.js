const resume = require("../../data/resume");

Page({
  data: {
    projects: resume.projects,
    awards: resume.awards,
    profile: resume.profile,
    ui: resume.ui,
    activeProject: 0
  },

  toggleProject(event) {
    const index = Number(event.currentTarget.dataset.index);

    this.setData({
      activeProject: this.data.activeProject === index ? -1 : index
    });
  },

  onShareAppMessage() {
    return {
      title: "\u8d44\u6d77\u6625\u7684\u7ecf\u5386\u4e0e\u8363\u8a89",
      path: "/pages/experience/experience"
    };
  }
});
