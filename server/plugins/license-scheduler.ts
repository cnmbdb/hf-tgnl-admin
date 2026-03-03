// 授权定时任务（已改为“永久激活，不再自动掉线”）
//
// 原逻辑：每天凌晨查询数据库 + 调 WordPress 接口做 IP / 过期校验，
//         不通过时会把 licenses 表里的 status 改成 inactive / expired，
//         导致你用着用着后台突然变成“未激活”，非常烦。
//
// 现在逻辑：不再做任何自动停用 / 过期处理。
// - 只在应用启动时打一条日志，说明自动校验已关闭；
// - 授权一旦通过 /license/activate-order.post 接口写入数据库并置为 active，
//   就不会被这个定时任务改回 inactive 或 expired 了。
//
// 如果以后需要“手动停用”，可以继续用 /license/deactivate.post 等接口手工操作。

export default async () => {
  console.log('[license-scheduler] 自动授权校验已关闭：激活一次后不再自动掉线、不再自动过期')
}
