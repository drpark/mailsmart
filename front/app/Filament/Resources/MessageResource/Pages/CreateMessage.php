<?php

namespace App\Filament\Resources\MessageResource\Pages;

use App\Filament\Resources\MessageResource;
use Filament\Resources\Pages\CreateRecord;
use Illuminate\Support\Facades\Http;
use App\Enums\EmotionType;
use Filament\Notifications\Notification;

class CreateMessage extends CreateRecord
{
    protected static string $resource = MessageResource::class;

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index');
    }

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $apiUrl = config('services.mailsmart.url') . '/predict';

        try {
            $response = Http::withoutVerifying()
                ->post($apiUrl, [
                    'text' => "{$data['title']} {$data['message']}"
                ]);

            if (!$response->successful()) {
                Notification::make()
                    ->danger()
                    ->title("Erreur lors de l'analyse du message")
                    ->body($response->json()['message'] ?? 'Erreur inconnue')
                    ->send();

                return $data;
            }

            $apiData = $response->json();

            $data['user_id'] = auth()->id();
            $data['is_spam'] = $apiData['is_spam'] ?? false;
            $data['emotion'] = EmotionType::tryFrom($apiData['emotion'] ?? 'neutral') ?? EmotionType::NEUTRAL;
            $data['is_real_spam'] = $data['is_spam'];
            $data['emotion_real'] = $data['emotion'];

            return $data;
        } catch (\Exception $e) {
            Notification::make()
                ->danger()
                ->title("Erreur lors de l'analyse du message")
                ->body($e->getMessage())
                ->send();

            return $data;
        }
    }
}
