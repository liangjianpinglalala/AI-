# 分镜脚本生成 Prompt（草稿）

## 目标

将 `content_retrieval` 步骤输出的结构化知识，转换成可直接驱动配音、画面生成、剪辑的分镜脚本。

## 输入

- `content_retrieval` 步骤的输出 JSON

## 输出 JSON Schema（草稿）

```json
{
  "style_prefix": "统一画风描述，如“中国水墨风格，工笔重彩，古风人物”",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "旁白文案",
      "subtitle": "字幕文本（可与旁白不同，字幕更简短）",
      "visual_prompt": "画面生成 prompt（会自动拼接 style_prefix）",
      "duration_hint_sec": 6,
      "transition": "fade | cut | dissolve"
    }
  ]
}
```

## 注意事项

- 建议节奏：开场引入 -> 逐句/逐层解析 -> 背景典故 -> 寓意/情感总结，场景数控制在 5-8 个，避免视频过长或过碎。
- `visual_prompt` 涉及同一人物反复出现时，需保持外貌描述一致，避免画面人物“跳变”。
