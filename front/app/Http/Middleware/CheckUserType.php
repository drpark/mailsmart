<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckUserType
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $user = auth()->user();

        if (!$user) {
            return redirect()->route('filament.user.auth.login');
        }

        // Si c'est un admin qui essaie d'accéder au panel user
        if ($user->type === 'admin' && $request->is('/')) {
            return redirect()->route('filament.admin.pages.dashboard');
        }

        // Si c'est un user qui essaie d'accéder au panel admin
        if ($user->type === 'user' && $request->is('admin*')) {
            return redirect()->route('filament.user.pages.dashboard');
        }

        return $next($request);
    }
}
