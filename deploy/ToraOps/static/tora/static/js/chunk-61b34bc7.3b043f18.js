(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-61b34bc7"],{"7a7d":function(t,e,n){"use strict";n("f59c")},9406:function(t,e,n){"use strict";n.r(e);var a=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{staticClass:"dashboard-container"},[n("div",{staticClass:"dashboard-text"},[n("span",[t._v("欢迎登录， "+t._s(t.name))])]),n("el-divider"),n("el-card",{staticClass:"box-card",attrs:{shadow:"hover"}},[n("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[n("span",[t._v("任务流概况")])]),n("div",[t._v(" 现在共有 "),n("el-tag",{key:t.count,attrs:{effect:"dark"}},[t._v(" "+t._s(t.count)+" ")]),t._v(" 个任务流")],1)]),n("el-divider"),n("el-timeline",t._l(t.activities,(function(e,a){return n("el-timeline-item",{key:a,attrs:{timestamp:e.timestamp,color:e.color}},[t._v(" "+t._s(e.content)+" ")])})),1)],1)},o=[],r=n("5530"),s=n("2f62"),c=n("a201"),i={name:"Dashboard",data:function(){return{count:"",activities:[{content:"任务流高级搜索",timestamp:"2021-03-10",color:"#0bbd87"},{content:"任务流添加和删除",timestamp:"2021-03-1",color:""},{content:"初版网站部署上线",timestamp:"2021-03"},{content:"网站后端前端基本设计完成",timestamp:"2021-02"},{content:"系统前后端架构设计",timestamp:"2021-01"}]}},computed:Object(r["a"])({},Object(s["b"])(["name","toraapp"])),mounted:function(){},created:function(){this.getUserInfo(),this.getTaskFlow()},methods:{getUserInfo:function(){this.$store.dispatch("choice/getChoice")},getTaskFlow:function(){var t=this;Object(c["a"])().then((function(e){t.count=e.count}))}}},u=i,d=(n("7a7d"),n("2877")),l=Object(d["a"])(u,a,o,!1,null,"b9169276",null);e["default"]=l.exports},a201:function(t,e,n){"use strict";n.d(e,"a",(function(){return o})),n.d(e,"d",(function(){return r})),n.d(e,"c",(function(){return s})),n.d(e,"e",(function(){return c})),n.d(e,"b",(function(){return i}));var a=n("b775");function o(t){return Object(a["a"])({url:"/task-flows/",method:"get",params:{page:t}})}function r(t,e){return Object(a["a"])({url:"/task-flows/",method:"get",params:{page:t,engine_room:e}})}function s(t,e){return Object(a["a"])({url:"/task-flows/",method:"get",params:{page:t,customer:e}})}function c(t,e){return Object(a["a"])({url:"/task-flows/",method:"get",params:{page:t,serial_number:e}})}function i(t,e,n,o,r,s,c,i){return Object(a["a"])({url:"/task-flows/",method:"get",params:{page:t,task_status:e,engine_room:n,serial_number:o,IT_checked_number:r,node_id:s,inner_ip:c,custgroup_name:i}})}},f59c:function(t,e,n){}}]);