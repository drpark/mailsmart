<?php

namespace App\Filament\Resources\App\Filament\ResourcesResource\Pages;

use App\Filament\Resources\App\Filament\ResourcesResource;
use Filament\Resources\Pages\Page;

class Dashboard extends Page
{
    protected static string $resource = ResourcesResource::class;

    protected static string $view = 'filament.resources.app..filament..resources-resource.pages.dashboard';
}
