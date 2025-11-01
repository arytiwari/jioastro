declare module 'react' {
  export type ReactNode = any
  export type FC<P = {}> = (props: P & { children?: ReactNode }) => ReactNode
  export type ComponentType<P = {}> = (props: P) => ReactNode
  export type MutableRefObject<T> = { current: T }
  export type Dispatch<A> = (value: A) => void
  export type SetStateAction<S> = S | ((prev: S) => S)
  export type RefCallback<T> = (instance: T | null) => void
  export type Ref<T> = MutableRefObject<T> | RefCallback<T> | null

  export function useState<S>(initialState: S | (() => S)): [S, Dispatch<SetStateAction<S>>]
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void
  export function useMemo<T>(factory: () => T, deps: any[]): T
  export function useCallback<T extends (...args: any[]) => any>(fn: T, deps: any[]): T
  export function useRef<T>(initialValue: T | null): MutableRefObject<T | null>
  export function useContext<T>(context: any): T
  export function createContext<T>(defaultValue: T): any
  export function forwardRef<T, P = {}>(render: (props: P, ref: Ref<T>) => ReactNode): ComponentType<P>
  export function useReducer<R extends (state: any, action: any) => any>(
    reducer: R,
    initialState: Parameters<R>[0],
    initializer?: (arg: Parameters<R>[0]) => any
  ): [ReturnType<R>, Dispatch<Parameters<R>[1]>]

  export const Fragment: any
  const React: {
    createElement: (...args: any[]) => any
  }
  export default React
}

declare module 'react/jsx-runtime' {
  export const jsx: any
  export const jsxs: any
  export const Fragment: any
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any
  }
}
