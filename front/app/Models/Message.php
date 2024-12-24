<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use App\Enums\EmotionType;
use Illuminate\Support\Facades\Http;
use Filament\Notifications\Notification;

class Message extends Model
{
    protected $fillable = [
        'user_id',
        'title',
        'message',
        'is_spam',
        'is_real_spam',
        'emotion',
        'emotion_real'
    ];

    protected $casts = [
        'is_spam' => 'boolean',
        'is_real_spam' => 'boolean',
        'emotion' => EmotionType::class,
        'emotion_real' => EmotionType::class,
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    protected static function booted()
    {
        static::updated(function ($message) {
            // On vérifie si les champs de correction ont été modifiés manuellement
            if ($message->isDirty(['is_real_spam', 'emotion_real'])) {
                $apiUrl = config('services.mailsmart.url') . '/feedback';

                try {
                    $response = Http::withoutVerifying()
                        ->post($apiUrl, [
                            'message_id' => $message->id,
                            'user_id' => $message->user_id,
                            'text' => "{$message->title} {$message->message}",
                            'initial_spam_prediction' => $message->getRawOriginal('is_spam'),
                            'initial_sentiment_prediction' => $message->getRawOriginal('emotion'),
                            'real_spam' => $message->is_real_spam,
                            'real_emotion' => $message->emotion_real->value
                        ]);

                    if (!$response->successful()) {
                        Notification::make()
                            ->warning()
                            ->title('Attention')
                            ->body("Le feedback n'a pas pu être envoyé à l'API")
                            ->send();
                    } else {
                        Notification::make()
                            ->success()
                            ->title('Feedback envoyé')
                            ->body('Merci pour votre contribution !')
                            ->send();
                    }
                } catch (\Exception $e) {
                    Notification::make()
                        ->danger()
                        ->title('Erreur')
                        ->body("Impossible d'envoyer le feedback : " . $e->getMessage())
                        ->send();
                }
            }
        });
    }
}
