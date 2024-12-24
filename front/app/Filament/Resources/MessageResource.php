<?php

namespace App\Filament\Resources;

use App\Filament\Resources\MessageResource\Pages;
use App\Models\Message;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use App\Enums\EmotionType;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\HtmlString;
use App\Traits\EmotionTranslation;

class MessageResource extends Resource
{
    use EmotionTranslation;

    protected static ?string $model = Message::class;
    protected static ?string $navigationIcon = 'heroicon-o-chat-bubble-left-right';
    protected static ?string $navigationLabel = 'Messages';
    protected static ?string $recordTitleAttribute = 'title';

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

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Hidden::make('user_id')
                    ->default(auth()->id()),

                Forms\Components\TextInput::make('title')
                    ->required()
                    ->maxLength(255)
                    ->label('Titre')
                    ->disabled(fn(?Model $record) => $record?->exists),

                Forms\Components\Textarea::make('message')
                    ->required()
                    ->label('Message')
                    ->columnSpanFull()
                    ->disabled(fn(?Model $record) => $record?->exists),

                Forms\Components\Section::make('Analyse du message')
                    ->description('Résultats de l\'analyse automatique et corrections')
                    ->visible(fn(?Model $record) => $record?->exists)
                    ->schema([
                        Forms\Components\Grid::make(2)
                            ->schema([
                                Forms\Components\Section::make('Détection automatique')
                                    ->schema([
                                        Forms\Components\Placeholder::make('is_spam_label')
                                            ->label('Spam détecté')
                                            ->content(fn(Message $record) => new HtmlString(
                                                view('filament.components.badge', [
                                                    'color' => $record->is_spam ? 'danger' : 'success',
                                                    'label' => $record->is_spam ? 'Oui' : 'Non',
                                                ])->render()
                                            )),

                                        Forms\Components\Placeholder::make('emotion_label')
                                            ->label('Émotion détectée')
                                            ->content(fn(Message $record) => new HtmlString(
                                                view('filament.components.badge', [
                                                    'color' => 'primary',
                                                    'label' => self::translateEmotion($record->emotion->value),
                                                ])->render()
                                            )),
                                    ]),

                                Forms\Components\Section::make('Corrections')
                                    ->schema([
                                        Forms\Components\Toggle::make('is_real_spam')
                                            ->label('Est-ce vraiment un spam ?')
                                            ->inline(false),

                                        Forms\Components\Select::make('emotion_real')
                                            ->label('Émotion réelle')
                                            ->options(collect(EmotionType::cases())->pluck('value', 'value')
                                                ->mapWithKeys(fn($value) => [$value => self::translateEmotion($value)])),
                                    ]),
                            ]),
                    ]),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->defaultSort('created_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('title')
                    ->label('Titre')
                    ->searchable()
                    ->searchable(['title'], isIndividual: true),
                Tables\Columns\TextColumn::make('message')
                    ->label('Message')
                    ->limit(50)
                    ->searchable()
                    ->searchable(['message'], isIndividual: true),
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
            ->persistSearchInSession()
            ->persistSortInSession()
            ->filters([])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListMessages::route('/'),
            'create' => Pages\CreateMessage::route('/create'),
            'edit' => Pages\EditMessage::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()->where('user_id', auth()->id());
    }
}
