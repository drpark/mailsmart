<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureUserRoleIsAllowed
{
    public function handle(Request $request, Closure $next, string $panel)
    {
        $user = auth()->user();

        if ($panel === 'admin' && $user?->type !== 'admin') {
            return redirect('/');
        }

        if ($panel === 'user' && $user?->type === 'admin') {
            return redirect('/admin');
        }

        return $next($request);
    }
}
