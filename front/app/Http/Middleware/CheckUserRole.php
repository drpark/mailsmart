<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckUserRole
{
    public function handle(Request $request, Closure $next, string $role): Response
    {
        if (auth()->user()?->type !== $role) {
            return $role === 'admin'
                ? redirect('/')
                : redirect('/admin');
        }

        return $next($request);
    }
}
