<?php

namespace App\Filament\Widgets;

use App\Models\Message;
use App\Enums\UserType;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class SpamAccuracyWidget extends BaseWidget
{
    public static function canView(): bool
    {
        return auth()->user()?->type === UserType::ADMIN;
    }

    protected function getStats(): array
    {
        $totalMessages = Message::count();

        if ($totalMessages === 0) {
            return [
                Stat::make('Précision Spam', '0%')
                    ->description('Aucun message')
                    ->color('gray'),
                Stat::make('Précision Émotion', '0%')
                    ->description('Aucun message')
                    ->color('gray'),
            ];
        }

        // Calcul précision Spam
        $correctSpamPredictions = Message::whereColumn('is_spam', 'is_real_spam')->count();
        $spamAccuracy = round(($correctSpamPredictions / $totalMessages) * 100, 2);

        // Calcul précision Émotion
        $correctEmotionPredictions = Message::whereColumn('emotion', 'emotion_real')->count();
        $emotionAccuracy = round(($correctEmotionPredictions / $totalMessages) * 100, 2);

        return [
            Stat::make('Précision Spam', $spamAccuracy . '%')
                ->description($correctSpamPredictions . ' prédictions correctes sur ' . $totalMessages)
                ->color($this->getColorForAccuracy($spamAccuracy)),

            Stat::make('Précision Émotion', $emotionAccuracy . '%')
                ->description($correctEmotionPredictions . ' prédictions correctes sur ' . $totalMessages)
                ->color($this->getColorForAccuracy($emotionAccuracy)),
        ];
    }

    private function getColorForAccuracy(float $accuracy): string
    {
        return match (true) {
            $accuracy >= 90 => 'success',
            $accuracy >= 70 => 'warning',
            default => 'danger',
        };
    }
}
