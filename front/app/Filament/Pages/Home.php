<?php

namespace App\Filament\Pages;

use App\Filament\Resources\MessageResource\Pages\ListMessages;

class Home extends ListMessages
{
    protected static ?string $navigationLabel = 'Accueil';
    protected static ?string $title = 'Messages';
    protected static ?string $navigationIcon = 'heroicon-o-home';
    protected static ?int $navigationSort = -2;
}
