<?php

namespace App\Enums;

enum EmotionType: string
{
    case ANGER = 'anger';
    case JOY = 'joy';
    case SADNESS = 'sadness';
    case NEUTRAL = 'neutral';
    case FEAR = 'fear';
    case SURPRISE = 'surprise';
}
