#!/usr/bin/env runghc

import Data.Maybe (fromJust)

type Alphabet a = [a]

type Interp a = [(a,Bool)]

data Expr a =
  Const a
  | NAND (Expr a) (Expr a)
  deriving Functor

instance Show a => Show (Expr a) where
  show (Const a) = show a
  show (NAND a b) = concat ["(", show a, " NAND ", show b, ")"]

exhaustExprDepth :: Alphabet a -> Int -> [Expr a]
exhaustExprDepth alph 0 = Const <$> alph
exhaustExprDepth alph n = [NAND a b | a <- prev, b <- prev] ++ prev
  where prev = exhaustExprDepth alph (n-1)

-- size :: Expr a -> Int
-- size (Const _) = 1
-- size (NAND x y) = 1 + size x + size y

evalExpr :: Eq a => Expr a -> Interp a -> Bool
evalExpr (Const x) t = fromJust $ lookup x t
evalExpr (NAND x y) t = not (xb && yb)
  where xb = evalExpr x t
        yb = evalExpr y t

genInterp :: Alphabet a -> [Interp a]
genInterp [] = [[]]
genInterp (x:xs) = [(x,b):rest | b <- [False, True], rest <- genInterp xs]

getTable :: Eq a => Alphabet a -> Expr a -> [Bool]
getTable alph e = evalExpr e <$> genInterp alph

main :: IO ()
main = mapM_ print $ filter isXOR (exhaustExprDepth b 3)
  where b = ["X", "Y"]
        isXOR expr = getTable b expr == [False, True, True, False]
