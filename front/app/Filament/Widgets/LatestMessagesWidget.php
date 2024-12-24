<?php

namespace App\Filament\Widgets;

use App\Models\Message;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;
use App\Enums\EmotionType;

class LatestMessagesWidget extends BaseWidget
{
    protected static ?int $sort = 2;

    protected int | string | array $columnSpan = 'full';

    protected static ?string $heading = 'Messages';

    public function table(Table $table): Table
    {
        return $table
            ->query(Message::query())
            ->defaultSort('created_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('title')
                    ->label('Titre')
                    ->searchable(),
                Tables\Columns\TextColumn::make('message')
                    ->label('Message')
                    ->limit(50)
                    ->searchable(),
                Tables\Columns\TextColumn::make('is_real_spam')
                    ->label('Spam')
                    ->formatStateUsing(fn(bool $state): string => $state ? 'Oui' : 'Non')
                    ->badge()
                    ->color(fn(bool $state): string => $state ? 'danger' : 'success'),
                Tables\Columns\TextColumn::make('emotion_real')
                    ->label('Émotion')
                    ->formatStateUsing(fn(?EmotionType $state) => $state ? self::translateEmotion($state->value) : '-')
                    ->badge()
                    ->color(fn(?EmotionType $state): string => $state ? self::getEmotionColor($state) : 'gray'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Date')
                    ->dateTime()
                    ->sortable(),
            ])
            ->actions([
                Tables\Actions\Action::make('edit')
                    ->label('Modifier')
                    ->url(fn(Message $record): string => route('filament.admin.resources.messages.edit', ['record' => $record]))
                    ->icon('heroicon-m-pencil-square'),
            ]);
    }

    protected static function translateEmotion(string $emotion): string
    {
        return match ($emotion) {
            'anger' => 'Colère',
            'joy' => 'Joie',
            'sadness' => 'Tristesse',
            'fear' => 'Peur',
            'surprise' => 'Surprise',
            default => 'Neutre'
        };
    }

    protected static function getEmotionColor(EmotionType $emotion): string
    {
        return match ($emotion) {
            EmotionType::ANGER => 'danger',
            EmotionType::JOY => 'success',
            EmotionType::SADNESS => 'info',
            EmotionType::FEAR => 'warning',
            EmotionType::SURPRISE => 'warning',
            default => 'gray'
        };
    }
}
