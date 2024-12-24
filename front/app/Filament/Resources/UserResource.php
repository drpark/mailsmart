<?php

namespace App\Filament\Resources;

use App\Filament\Resources\UserResource\Pages;
use App\Models\User;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use App\Enums\UserType;
use Illuminate\Support\Carbon;

class UserResource extends Resource
{
    protected static ?string $model = User::class;
    protected static ?string $navigationIcon = 'heroicon-o-users';
    protected static ?string $navigationLabel = 'Utilisateurs';

    public static function form(Form $form): Form
    {
        return $form
            ->model(User::class)
            ->schema([
                Forms\Components\TextInput::make('name')
                    ->required()
                    ->label('Nom'),
                Forms\Components\TextInput::make('email')
                    ->email()
                    ->required(),
                Forms\Components\Select::make('type')
                    ->options([
                        'user' => 'Utilisateur',
                        'admin' => 'Administrateur'
                    ])
                    ->required(),
                Forms\Components\Checkbox::make('email_verified')
                    ->label('Email vérifié')
                    ->afterStateHydrated(function (Forms\Components\Checkbox $component, $state, $livewire) {

                        if ($livewire->record) {
                            $component->state($livewire->record->hasVerifiedEmail());
                        }
                    })
                    ->afterStateUpdated(function ($state, $livewire) {
                        if ($state) {
                            $livewire->record->markEmailAsVerified();
                            $livewire->record->save(); // Assurez-vous de sauvegarder
                        } else {
                            $livewire->record->forceFill([
                                'email_verified_at' => null
                            ])->save();
                        }
                    })
                    ->live(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nom')
                    ->searchable(),
                Tables\Columns\TextColumn::make('email')
                    ->searchable(),
                Tables\Columns\TextColumn::make('type')
                    ->badge()
                    ->color(fn(UserType $state): string => match ($state) {
                        UserType::ADMIN => 'success',
                        UserType::USER => 'info',
                    }),
                Tables\Columns\IconColumn::make('email_verified_at')
                    ->label('Email vérifié')
                    ->boolean()
                    ->trueIcon('heroicon-o-check-circle')
                    ->falseIcon('heroicon-o-x-circle'),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\Action::make('verify_email')
                    ->label('Vérifier email')
                    ->icon('heroicon-o-check')
                    ->requiresConfirmation()
                    ->visible(fn(User $record) => !$record->hasVerifiedEmail())
                    ->action(function (User $record) {
                        $record->markEmailAsVerified();
                    }),
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListUsers::route('/'),
            'create' => Pages\CreateUser::route('/create'),
            'edit' => Pages\EditUser::route('/{record}/edit'),
        ];
    }

    public static function getNavigationGroup(): ?string
    {
        return 'Administration';
    }
}
