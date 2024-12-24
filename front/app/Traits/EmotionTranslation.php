<?php

namespace App\Traits;

trait EmotionTranslation
{
    public static function translateEmotion(string $emotion): string
    {
        return match ($emotion) {
            'anger' => 'Colère',
            'joy' => 'Joie',
            'sadness' => 'Tristesse',
            'neutral' => 'Neutre',
            'fear' => 'Peur',
            'surprise' => 'Surprise',
            default => $emotion,
        };
    }
}
