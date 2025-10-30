import * as React from 'react'

type QueryKey = string | readonly unknown[]

function serializeSegment(segment: unknown): string {
  if (segment === null) return 'null'
  switch (typeof segment) {
    case 'string':
      return segment
    case 'number':
    case 'boolean':
    case 'bigint':
      return String(segment)
    default:
      try {
        return JSON.stringify(segment)
      } catch {
        return String(segment)
      }
  }
}

function keyToSegments(key: QueryKey): string[] {
  if (Array.isArray(key)) {
    return key.map(serializeSegment)
  }
  return [serializeSegment(key)]
}

function hashKey(key: QueryKey): string {
  return keyToSegments(key).join('||')
}

interface QueryState<TData = unknown> {
  data?: TData
  error?: unknown
  status: 'idle' | 'loading' | 'success' | 'error'
  updatedAt: number
}

type Listener = () => void

export class QueryClient {
  private cache = new Map<string, QueryState>()
  private listeners = new Map<string, Set<Listener>>()

  private ensureState(key: QueryKey): QueryState {
    const hashed = hashKey(key)
    const existing = this.cache.get(hashed)
    if (existing) return existing
    const state: QueryState = { status: 'idle', updatedAt: Date.now() }
    this.cache.set(hashed, state)
    return state
  }

  private notify(hashedKey: string) {
    const listeners = this.listeners.get(hashedKey)
    if (!listeners) return
    for (const listener of Array.from(listeners)) {
      listener()
    }
  }

  getQueryState<TData = unknown>(key: QueryKey): QueryState<TData> | undefined {
    const hashed = hashKey(key)
    return this.cache.get(hashed) as QueryState<TData> | undefined
  }

  getQueryData<TData = unknown>(key: QueryKey): TData | undefined {
    return this.getQueryState<TData>(key)?.data
  }

  setQueryData<TData = unknown>(key: QueryKey, data: TData) {
    const hashed = hashKey(key)
    const state = this.ensureState(key)
    state.data = data
    state.error = undefined
    state.status = 'success'
    state.updatedAt = Date.now()
    this.cache.set(hashed, state)
    this.notify(hashed)
  }

  setQueryError(key: QueryKey, error: unknown) {
    const hashed = hashKey(key)
    const state = this.ensureState(key)
    state.error = error
    state.status = 'error'
    state.updatedAt = Date.now()
    this.cache.set(hashed, state)
    this.notify(hashed)
  }

  setQueryLoading(key: QueryKey) {
    const hashed = hashKey(key)
    const state = this.ensureState(key)
    state.status = 'loading'
    state.updatedAt = Date.now()
    this.cache.set(hashed, state)
    this.notify(hashed)
  }

  subscribe(key: QueryKey, listener: Listener): () => void {
    const hashed = hashKey(key)
    const listeners = this.listeners.get(hashed) ?? new Set<Listener>()
    listeners.add(listener)
    this.listeners.set(hashed, listeners)
    return () => {
      const current = this.listeners.get(hashed)
      if (!current) return
      current.delete(listener)
      if (current.size === 0) {
        this.listeners.delete(hashed)
      }
    }
  }

  invalidateQueries(partialKey: QueryKey) {
    const prefix = hashKey(partialKey)
    const prefixWithSeparator = `${prefix}||`

    for (const hashed of Array.from(this.cache.keys())) {
      if (hashed === prefix || hashed.startsWith(prefixWithSeparator)) {
        this.cache.delete(hashed)
        this.notify(hashed)
      }
    }
  }

  clear() {
    this.cache.clear()
    this.listeners.clear()
  }
}

interface QueryClientContextValue {
  client: QueryClient
}

const QueryClientContext = React.createContext<QueryClientContextValue | null>(null)

export interface QueryClientProviderProps {
  client: QueryClient
  children: React.ReactNode
}

export function QueryClientProvider({ client, children }: QueryClientProviderProps) {
  const value = React.useMemo(() => ({ client }), [client])
  return <QueryClientContext.Provider value={value}>{children}</QueryClientContext.Provider>
}

export function useQueryClient(): QueryClient {
  const context = React.useContext(QueryClientContext)
  if (!context) {
    throw new Error('useQueryClient must be used within a QueryClientProvider')
  }
  return context.client
}

interface UseQueryOptions<TData> {
  queryKey: QueryKey
  queryFn: () => Promise<TData>
  enabled?: boolean
  initialData?: TData
}

interface UseQueryResult<TData> {
  data: TData | undefined
  error: unknown
  isLoading: boolean
  isError: boolean
  status: QueryState['status']
  refetch: () => Promise<TData | undefined>
}

export function useQuery<TData>({
  queryKey,
  queryFn,
  enabled = true,
  initialData,
}: UseQueryOptions<TData>): UseQueryResult<TData> {
  const client = useQueryClient()
  const keyHash = React.useMemo(() => hashKey(queryKey), [queryKey])
  const [state, setState] = React.useState<QueryState<TData>>(() => {
    const existing = client.getQueryState<TData>(queryKey)
    if (existing) {
      return existing
    }
    if (typeof initialData !== 'undefined') {
      client.setQueryData(queryKey, initialData)
      return client.getQueryState<TData>(queryKey) as QueryState<TData>
    }
    return { status: enabled ? 'loading' : 'idle', updatedAt: Date.now() }
  })
  const [revision, setRevision] = React.useState(0)

  const runQuery = React.useCallback(async () => {
    if (!enabled) return client.getQueryData<TData>(queryKey)
    client.setQueryLoading(queryKey)
    setState(client.getQueryState<TData>(queryKey) as QueryState<TData>)

    try {
      const data = await queryFn()
      client.setQueryData(queryKey, data)
      const nextState = client.getQueryState<TData>(queryKey) as QueryState<TData>
      setState(nextState)
      return data
    } catch (error) {
      client.setQueryError(queryKey, error)
      const nextState = client.getQueryState<TData>(queryKey) as QueryState<TData>
      setState(nextState)
      return undefined
    }
  }, [client, enabled, queryFn, queryKey])

  React.useEffect(() => {
    const unsubscribe = client.subscribe(queryKey, () => {
      setRevision((value) => value + 1)
    })
    return unsubscribe
  }, [client, queryKey])

  React.useEffect(() => {
    const current = client.getQueryState<TData>(queryKey)
    if (!current || current.status === 'idle') {
      runQuery()
      return
    }
    setState(current)
    if (enabled && current.status === 'error') {
      runQuery()
    }
  }, [client, queryKey, revision, enabled, runQuery])

  return {
    data: state.data,
    error: state.error,
    isLoading: state.status === 'loading' || state.status === 'idle',
    isError: state.status === 'error',
    status: state.status,
    refetch: runQuery,
  }
}

interface UseMutationOptions<TData, TVariables> {
  mutationFn: (variables: TVariables) => Promise<TData>
  onSuccess?: (
    data: TData,
    variables: TVariables,
    context: { queryClient: QueryClient }
  ) => void
  onError?: (
    error: unknown,
    variables: TVariables,
    context: { queryClient: QueryClient }
  ) => void
  onSettled?: (
    data: TData | undefined,
    error: unknown,
    variables: TVariables,
    context: { queryClient: QueryClient }
  ) => void
}

interface UseMutationResult<TData, TVariables> {
  mutate: (variables: TVariables) => void
  mutateAsync: (variables: TVariables) => Promise<TData>
  reset: () => void
  data: TData | undefined
  error: unknown
  isPending: boolean
  isError: boolean
  isSuccess: boolean
}

export function useMutation<TData, TVariables = void>(
  options: UseMutationOptions<TData, TVariables>
): UseMutationResult<TData, TVariables> {
  const client = useQueryClient()
  const { mutationFn, onError, onSettled, onSuccess } = options
  const [status, setStatus] = React.useState<'idle' | 'pending' | 'success' | 'error'>('idle')
  const [data, setData] = React.useState<TData | undefined>(undefined)
  const [error, setError] = React.useState<unknown>(undefined)

  const execute = React.useCallback(
    async (variables: TVariables) => {
      setStatus('pending')
      setError(undefined)
      try {
        const result = await mutationFn(variables)
        setData(result)
        setStatus('success')
        onSuccess?.(result, variables, { queryClient: client })
        onSettled?.(result, undefined, variables, { queryClient: client })
        return result
      } catch (err) {
        setError(err)
        setStatus('error')
        onError?.(err, variables, { queryClient: client })
        onSettled?.(undefined, err, variables, { queryClient: client })
        throw err
      }
    },
    [client, mutationFn, onError, onSettled, onSuccess]
  )

  const mutate = React.useCallback(
    (variables: TVariables) => {
      void execute(variables)
    },
    [execute]
  )

  const reset = React.useCallback(() => {
    setStatus('idle')
    setData(undefined)
    setError(undefined)
  }, [])

  return {
    mutate,
    mutateAsync: execute,
    reset,
    data,
    error,
    isPending: status === 'pending',
    isError: status === 'error',
    isSuccess: status === 'success',
  }
}
