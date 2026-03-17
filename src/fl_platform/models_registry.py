"""Registry of available models and their parameters for each executor type."""

LLM_MODELS = {
    "claude-sonnet-4-6-20250620": {"display": "Claude Sonnet 4.6"},
    "claude-opus-4-6-20250620": {"display": "Claude Opus 4.6"},
    "gemini-2.5-pro": {"display": "Gemini 2.5 Pro"},
}

FAL_IMAGE_MODELS = {
    "fal-ai/nano-banana": {
        "display": "Nano Banana",
        "params": {
            "aspect_ratio": {
                "type": "select",
                "options": ["auto", "1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"],
                "default": "1:1",
                "description": "Aspect ratio of the generated image",
            },
            "num_images": {
                "type": "int", "min": 1, "max": 4, "default": 1,
                "description": "Number of images to generate (1-4)",
            },
            "output_format": {
                "type": "select", "options": ["png", "jpeg", "webp"], "default": "png",
                "description": "Output image format",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness (1=strict, 6=relaxed)",
            },
            "limit_generations": {
                "type": "bool", "default": False,
                "description": "Limit to 1 generation per prompt round, ignoring prompt instructions",
            },
        },
    },
    "fal-ai/nano-banana/edit": {
        "display": "Nano Banana (Image Edit)",
        "params": {
            "aspect_ratio": {
                "type": "select",
                "options": ["auto", "1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"],
                "default": "1:1",
                "description": "Aspect ratio of the generated image",
            },
            "num_images": {
                "type": "int", "min": 1, "max": 4, "default": 1,
                "description": "Number of images to generate",
            },
            "output_format": {
                "type": "select", "options": ["png", "jpeg", "webp"], "default": "png",
                "description": "Output image format",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness (1=strict, 6=relaxed)",
            },
        },
    },
    "fal-ai/nano-banana-2": {
        "display": "Nano Banana 2",
        "params": {
            "aspect_ratio": {
                "type": "select",
                "options": ["auto", "1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"],
                "default": "auto",
                "description": "Aspect ratio ('auto' lets the model choose)",
            },
            "resolution": {
                "type": "select", "options": ["1K", "2K", "4K"], "default": "1K",
                "description": "Native output resolution (not upscaled)",
            },
            "num_images": {
                "type": "int", "min": 1, "max": 4, "default": 1,
                "description": "Number of images to generate (1-4)",
            },
            "output_format": {
                "type": "select", "options": ["png", "jpeg", "webp"], "default": "png",
                "description": "Output image format",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness (1=strict, 6=relaxed)",
            },
            "enable_web_search": {
                "type": "bool", "default": False,
                "description": "Enable Google Search grounding before generation (+$0.015)",
            },
            "thinking_level": {
                "type": "select", "options": ["none", "minimal", "high"], "default": "none",
                "description": "Model reasoning depth ('none' disables, 'high' +$0.002)",
            },
            "limit_generations": {
                "type": "bool", "default": False,
                "description": "Limit to 1 generation per prompt round",
            },
        },
    },
    "fal-ai/nano-banana-2/edit": {
        "display": "Nano Banana 2 (Image Edit)",
        "params": {
            "aspect_ratio": {
                "type": "select",
                "options": ["auto", "1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"],
                "default": "auto",
                "description": "Aspect ratio",
            },
            "resolution": {
                "type": "select", "options": ["1K", "2K", "4K"], "default": "1K",
                "description": "Native output resolution",
            },
            "num_images": {
                "type": "int", "min": 1, "max": 4, "default": 1,
                "description": "Number of images to generate",
            },
            "output_format": {
                "type": "select", "options": ["png", "jpeg", "webp"], "default": "png",
                "description": "Output image format",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness",
            },
            "enable_web_search": {
                "type": "bool", "default": False,
                "description": "Enable Google Search grounding",
            },
            "thinking_level": {
                "type": "select", "options": ["none", "minimal", "high"], "default": "none",
                "description": "Model reasoning depth",
            },
        },
    },
    "fal-ai/flux/dev": {
        "display": "Flux Dev",
        "params": {
            "image_size": {
                "type": "select",
                "options": ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
                "default": "landscape_4_3",
                "description": "Output image size preset",
            },
            "num_inference_steps": {
                "type": "int", "min": 1, "max": 50, "default": 28,
                "description": "Number of denoising steps",
            },
            "guidance_scale": {
                "type": "float", "min": 1.0, "max": 20.0, "default": 3.5,
                "description": "Prompt adherence strength",
            },
            "num_images": {
                "type": "int", "min": 1, "max": 4, "default": 1,
                "description": "Number of images to generate",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed for reproducibility",
            },
        },
    },
    "fal-ai/flux-pro/v1.1-ultra": {
        "display": "Flux Pro 1.1 Ultra",
        "params": {
            "aspect_ratio": {
                "type": "select",
                "options": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "9:21"],
                "default": "16:9",
                "description": "Aspect ratio",
            },
            "output_format": {
                "type": "select", "options": ["png", "jpeg"], "default": "png",
                "description": "Output format",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed",
            },
        },
    },
    "fal-ai/recraft-v3": {
        "display": "Recraft V3",
        "params": {
            "image_size": {
                "type": "select",
                "options": ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
                "default": "landscape_4_3",
                "description": "Output image size preset",
            },
            "style": {
                "type": "select",
                "options": ["any", "realistic_image", "digital_illustration", "vector_illustration", "icon"],
                "default": "realistic_image",
                "description": "Image style",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed",
            },
        },
    },
}

FAL_VIDEO_MODELS = {
    "fal-ai/kling-video/v3/standard/text-to-video": {
        "display": "Kling 3.0 Standard (Text-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence (lower=creative, higher=strict)",
            },
            "negative_prompt": {
                "type": "text", "default": "blur, distort, and low quality",
                "description": "Elements to avoid in generation",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio (Chinese/English voice)",
            },
        },
    },
    "fal-ai/kling-video/v3/pro/text-to-video": {
        "display": "Kling 3.0 Pro (Text-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "blur, distort, and low quality",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio",
            },
        },
    },
    "fal-ai/kling-video/v3/standard/image-to-video": {
        "display": "Kling 3.0 Standard (Image-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "blur, distort, and low quality",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio",
            },
        },
    },
    "fal-ai/kling-video/v3/pro/image-to-video": {
        "display": "Kling 3.0 Pro (Image-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "blur, distort, and low quality",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio",
            },
        },
    },
    "fal-ai/kling-video/o1/standard/image-to-video": {
        "display": "Kling O1 Standard (Image-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1", "auto"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio (Chinese/English)",
            },
        },
    },
    "fal-ai/kling-video/o1/standard/reference-to-video": {
        "display": "Kling O1 Standard (Reference-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1", "auto"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio",
            },
        },
    },
    "fal-ai/kling-video/o1/image-to-video": {
        "display": "Kling O1 Pro (First/Last Frame to Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["5", "10"], "default": "5",
                "description": "Video duration in seconds",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16", "1:1", "auto"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "cfg_scale": {
                "type": "float", "min": 0.0, "max": 1.0, "default": 0.5,
                "description": "Prompt adherence",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate native audio",
            },
        },
    },
    "fal-ai/veo3": {
        "display": "Veo 3",
        "params": {
            "duration": {
                "type": "select", "options": ["4s", "6s", "8s"], "default": "8s",
                "description": "Video duration",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "resolution": {
                "type": "select", "options": ["720p", "1080p"], "default": "720p",
                "description": "Output resolution",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate audio for the video",
            },
            "enhance_prompt": {
                "type": "bool", "default": False,
                "description": "Auto-enrich prompt with cinematographic terminology",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid in generation",
            },
            "auto_fix": {
                "type": "bool", "default": True,
                "description": "Auto-rewrite prompts that fail content policy",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed",
            },
        },
    },
    "fal-ai/veo3/fast": {
        "display": "Veo 3 Fast",
        "params": {
            "duration": {
                "type": "select", "options": ["4s", "6s", "8s"], "default": "8s",
                "description": "Video duration",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "resolution": {
                "type": "select", "options": ["720p", "1080p"], "default": "720p",
                "description": "Output resolution",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate audio",
            },
            "enhance_prompt": {
                "type": "bool", "default": False,
                "description": "Auto-enrich prompt with cinematographic terminology",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed",
            },
        },
    },
    "fal-ai/veo3/image-to-video": {
        "display": "Veo 3 (Image-to-Video)",
        "params": {
            "duration": {
                "type": "select", "options": ["4s", "6s", "8s"], "default": "8s",
                "description": "Video duration",
            },
            "aspect_ratio": {
                "type": "select", "options": ["16:9", "9:16"], "default": "16:9",
                "description": "Video aspect ratio",
            },
            "resolution": {
                "type": "select", "options": ["720p", "1080p"], "default": "720p",
                "description": "Output resolution",
            },
            "generate_audio": {
                "type": "bool", "default": True,
                "description": "Generate audio",
            },
            "negative_prompt": {
                "type": "text", "default": "",
                "description": "Elements to avoid",
            },
            "safety_tolerance": {
                "type": "select", "options": ["1", "2", "3", "4", "5", "6"], "default": "4",
                "description": "Content moderation strictness",
            },
            "seed": {
                "type": "int", "min": 0, "max": 2147483647, "default": None,
                "description": "Random seed",
            },
        },
    },
    "fal-ai/minimax/video-01-live": {
        "display": "Minimax Video 01 Live",
        "params": {
            "prompt_optimizer": {
                "type": "bool", "default": True,
                "description": "Optimize prompt for better results",
            },
        },
    },
}


def get_models_for_executor(executor_type: str) -> dict:
    """Return model registry for given executor type."""
    if executor_type == "llm":
        return LLM_MODELS
    elif executor_type == "fal_image":
        return FAL_IMAGE_MODELS
    elif executor_type == "fal_video":
        return FAL_VIDEO_MODELS
    return {}
