<?php

namespace App\Filament\Pages;

use Filament\Pages\Dashboard as BaseDashboard;

class Dashboard extends BaseDashboard
{
    protected static ?string $navigationIcon = 'heroicon-o-home';
    protected static ?string $navigationLabel = 'Tableau de bord';
    protected static ?string $title = 'Tableau de bord';

    protected function getHeaderWidgets(): array
    {
        return [
            \App\Filament\Widgets\SpamAccuracyWidget::class,
        ];
    }

    protected function getFooterWidgets(): array
    {
        return [];
    }
}
