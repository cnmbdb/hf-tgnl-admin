import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

export default defineEventHandler(async (event) => {
  try {
    const keywordRepliesPath = join(process.cwd(), 'nl-2333', 'keyword_replies.json')
    
    if (!existsSync(keywordRepliesPath)) {
      // 如果文件不存在，返回默认的关键词回复配置
      const defaultReplies = {
        commands: {
          "/start": [
            {
              id: "start_text",
              type: "text",
              content: "您好，{username}\n欢迎使用自动充值会员机器人\n您的平台ID:{user_id}",
              order: 1
            },
            {
              id: "start_image_buttons",
              type: "image_text_buttons",
              image: "photo.jpg",
              content: "🟢 本机器人为您提供【24小时·Telegram会员】自助开通服务\n请选择下方按钮:",
              buttons: [
                [
                  { text: "🌟此账号开通", callback_data: "buy_myself" },
                  { text: "🎁为他人开通", callback_data: "buy_ship" }
                ],
                [
                  { text: "🔸会员价格🔸", callback_data: "buy_price" }
                ],
                [
                  { text: "🔸批量开会员🔸", callback_data: "buy_ship" }
                ]
              ],
              order: 2
            }
          ],
          "查询后台信息": [
            {
              id: "query_backend_text",
              type: "text",
              content: "📊 后台系统信息\n\n正在查询后台配置和状态信息...",
              order: 1
            }
          ]
        },
        buttons: {
          "🌟购买会员": [
            {
              id: "buy_member_image_buttons",
              type: "image_text_buttons",
              image: "photo.jpg",
              content: "🟢 本机器人为您提供【24小时·Telegram会员】自助开通服务\n请选择下方按钮:",
              buttons: [
                [
                  { text: "🌟此账号开通", callback_data: "buy_myself" },
                  { text: "🎁为他人开通", callback_data: "buy_ship" }
                ],
                [
                  { text: "🔸会员价格🔸", callback_data: "buy_price" }
                ],
                [
                  { text: "🔸批量开会员🔸", callback_data: "buy_ship" }
                ]
              ],
              order: 1
            }
          ],
          "👩联系客服": [
            {
              id: "contact_service_buttons",
              type: "text_buttons",
              content: "请点击下方按钮跳转：",
              buttons: [
                [
                  { text: "联系客服", url: "{CUSTOMER_SERVICE_ID}" }
                ]
              ],
              order: 1
            }
          ],
          "⚡️我要充值": [
            {
              id: "recharge_buttons",
              type: "text_buttons",
              content: "💰 请选择充值金额：",
              buttons: [
                [
                  { text: "20", callback_data: "20" },
                  { text: "40", callback_data: "40" },
                  { text: "60", callback_data: "60" },
                  { text: "80", callback_data: "80" },
                  { text: "100", callback_data: "100" }
                ],
                [
                  { text: "33", callback_data: "33" },
                  { text: "66", callback_data: "66" },
                  { text: "99", callback_data: "99" },
                  { text: "132", callback_data: "132" },
                  { text: "165", callback_data: "165" }
                ],
                [
                  { text: "49", callback_data: "49" },
                  { text: "98", callback_data: "98" },
                  { text: "147", callback_data: "147" },
                  { text: "196", callback_data: "196" },
                  { text: "245", callback_data: "245" }
                ]
              ],
              order: 1
            }
          ],
          "👤个人中心": [
            {
              id: "personal_center_text",
              type: "text",
              content: "👤 *个人中心*\n\n您的平台ID：{chat_id}\n当前余额：{balance} USDT\n注册时间：{register_time}\n\n感谢您的使用！",
              order: 1
            }
          ],
          "📦笔数套餐": [
            {
              id: "bishu_package_intro",
              type: "text_buttons",
              content: "本功能为笔数套餐，规则:\n添加地址后并激活对应套餐，如套餐地址一小时内不持续转账消耗能量，则自动休眠，如再使用套餐 需再次点击激活按钮",
              buttons: [
                [
                  { text: "已有套餐", callback_data: "bishu_existing" },
                  { text: "添加套餐", callback_data: "bishu_add" }
                ]
              ],
              order: 1
            },
            {
              id: "bishu_package_select",
              type: "text_buttons",
              content: "请选择笔数套餐笔数(不限时间)",
              buttons: [
                [
                  { text: "5笔/15T", callback_data: "bishu_pkg_5_15" },
                  { text: "15笔/45T", callback_data: "bishu_pkg_15_45" }
                ],
                [
                  { text: "50笔/150T", callback_data: "bishu_pkg_50_150" },
                  { text: "100笔/300T", callback_data: "bishu_pkg_100_300" }
                ]
              ],
              order: 2
            },
            {
              id: "bishu_package_input",
              type: "text",
              content: "请输入并发送给我您的绑定钱包地址",
              order: 3
            },
            {
              id: "bishu_package_payment",
              type: "text_buttons",
              content: "请选择支付方式",
              buttons: [
                [
                  { text: "使用余额", callback_data: "bishu_pay_balance" },
                  { text: "立即支付", callback_data: "bishu_pay_now" }
                ]
              ],
              order: 4
            },
            {
              id: "bishu_package_addresses",
              type: "text_buttons",
              content: "已添加以下地址",
              buttons: [],
              order: 5
            }
          ]
        }
      }
      
      return {
        success: true,
        data: defaultReplies
      }
    }
    
    const data = readFileSync(keywordRepliesPath, 'utf-8')
    const keywordReplies = JSON.parse(data)
    
    return {
      success: true,
      data: keywordReplies
    }
  } catch (error) {
    console.error('获取关键词回复失败:', error)
    return {
      success: false,
      error: '获取关键词回复失败'
    }
  }
})